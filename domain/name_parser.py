from __future__ import annotations
from typing import List, Tuple
import unicodedata

from domain.contact import Contact
from domain import constants


def _split_first_last(name_tokens: List[str]) -> Tuple[str, str]:
    """
    Fallback-Split:
      - Letztes Token(-Block) = Nachname.
      - Rückwärts werden CONNECTORS (constants.SURNAME_CONNECTORS)
        vorangestellt, wenn sie passen.
      - Rest = Vorname.
    """
    if not name_tokens:
        return "", ""
    idx_last = len(name_tokens) - 1
    last = [name_tokens[idx_last]]
    j = idx_last - 1
    while j >= 0:
        t = name_tokens[j].rstrip(".").lower()
        # Zwei-Wort-Connector prüfen
        if j < idx_last:
            two = f"{name_tokens[j].lower()} {name_tokens[j+1].lower()}"
            if two in constants.SURNAME_CONNECTORS:
                last.insert(0, name_tokens[j])
                j -= 1
                continue
        if t in constants.SURNAME_CONNECTORS:
            last.insert(0, name_tokens[j])
            j -= 1
            continue
        break
    vor = name_tokens[: j + 1] if j >= 0 else []
    return " ".join(vor), " ".join(last)


def parse_name_to_contact(input_str: str, title_repo) -> Contact:
    """
    Zerlegt Freitext in ein Contact-Objekt.
    - Unicode-Normalisierung
    - dynamische Titel aus title_repo.lookup()
    - Title-Casing von Vor- und Nachname
    """
    contact = Contact()
    if not input_str or not input_str.strip():
        return contact

    # Unicode-Normalisierung
    normalized = unicodedata.normalize("NFC", input_str.strip())

    # 0.5) Comma-Separated Handling
    if "," in normalized:
        parts = [p.strip() for p in normalized.split(",", 1)]
        prefix_tokens = parts[0].replace(",", "").split()
        suffix_tokens = parts[1].replace(",", "").split()
        first_clean = prefix_tokens[0].rstrip(".").lower() if prefix_tokens else ""
        if first_clean in constants.SALUTATIONS or title_repo.lookup(first_clean):
            tokens = prefix_tokens.copy()
            sal_token = None
            if tokens and tokens[0].rstrip(".").lower() in constants.SALUTATIONS:
                sal_token = tokens.pop(0)
            title_tokens: List[str] = []
            while tokens and title_repo.lookup(tokens[0].rstrip(".").lower()):
                title_tokens.append(tokens.pop(0))
            last_name_tokens = tokens
            new_tokens: List[str] = []
            if sal_token:
                new_tokens.append(sal_token)
            new_tokens.extend(title_tokens)
            new_tokens.extend(suffix_tokens)
            new_tokens.extend(last_name_tokens)
            return parse_name_to_contact(" ".join(new_tokens), title_repo)

    # Tokenisierung (Kommas entfernt)
    tokens = normalized.replace(",", "").split()

    # Anrede/Saluation
    if tokens:
        key = tokens[0].rstrip(".").lower()
        if key in constants.SALUTATIONS:
            sal = constants.SALUTATIONS[key]
            contact.anrede = tokens.pop(0).rstrip(".")
            contact.geschlecht = sal["gender"]
            contact.sprache = sal["language"]

    # Mehrwortige Titel-Erkennung (inkl. Abkürzungen)
    # Build map: key→short_form and normalized short_form→short_form
    known_map: dict[str, str] = {}
    for key in title_repo.get_titles():
        short = title_repo.lookup(key) or key
        known_map[key] = short
        norm = short.replace(".", "").replace("-", " ").strip().lower()
        known_map[norm] = short

    titles: List[str] = []
    i = 0
    max_seq = max(len(k.split()) for k in known_map.keys())
    while i < len(tokens):
        matched = False
        # try longest possible sequences first
        for seq_len in range(min(max_seq, len(tokens) - i), 0, -1):
            candidate = " ".join(tokens[i : i + seq_len])
            clean = candidate.replace(".", "").replace("-", " ").strip().lower()
            if clean in known_map:
                titles.append(known_map[clean])
                i += seq_len
                matched = True
                break
        if not matched:
            break
    tokens = tokens[i:]
    contact.titel = " ".join(titles)

    # Extra-Titel im Rest erkennen
    remaining = [t.rstrip(".").lower() for t in tokens]
    for tok in remaining:
        if tok in known_map:
            contact.inaccuracies.append(f"Titel im Namen gefunden: „{tok}“")
            break

    low_tokens = [t.lower() for t in tokens]
    for part in sorted(constants.SURNAME_CONNECTORS, key=lambda p: len(p.split()), reverse=True):
        part_toks = part.split()
        for i in range(len(tokens) - len(part_toks) + 1):
            if low_tokens[i : i + len(part_toks)] == part_toks:
                # z.B. ["von","hallo-mia"] → Vorname="", Nachname="von hallo-mia"
                contact.vorname = " ".join(tokens[:i])
                contact.nachname = " ".join(tokens[i:])
                # direkt raus, nicht weiter splitten
                contact.vorname = unicodedata.normalize("NFC", contact.vorname).title()
                contact.nachname = unicodedata.normalize("NFC", contact.nachname).title()
                return contact

    # Explizite Hyphen-Regel: ab erstem Bindestrich des letzten Tokens (Weil es ja auch Vornamen mit Bindestrich geben kann)
    last_tok = tokens[-1]
    if "-" in last_tok:
        contact.vorname = " ".join(tokens[:-1])
        contact.nachname = last_tok
    else:
        # 6) Ein-Token-Fall
        if len(tokens) == 1:
            contact.nachname = tokens[0]
        else:
            # 7) Fallback-Split
            vor, nach = _split_first_last(tokens)
            contact.vorname, contact.nachname = vor, nach

    # Title-Casing & Finale Normalisierung
    contact.vorname = unicodedata.normalize("NFC", contact.vorname).title()
    contact.nachname = unicodedata.normalize("NFC", contact.nachname).title()
    return contact
