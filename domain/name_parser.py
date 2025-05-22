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

    # 0) Tokenisierung (Kommas entfernt)
    tokens = normalized.replace(",", "").split()

    # 1) Anrede/Saluation
    if tokens:
        key = tokens[0].rstrip(".").lower()
        if key in constants.SALUTATIONS:
            sal = constants.SALUTATIONS[key]
            contact.anrede = tokens.pop(0).rstrip(".")
            contact.geschlecht = sal["gender"]
            contact.sprache = sal["language"]

    # 2) Titel (dynamisch aus title_repo)
    titles: List[str] = []
    while tokens:
        clean = tokens[0].rstrip(".").lower()
        kurz = title_repo.lookup(clean)
        if not kurz:
            break
        tokens.pop(0)
        titles.append(kurz)
    contact.titel = " ".join(titles)

    # Wenn nichts übrig bleibt, fertig
    if not tokens:
        return contact

    # 3) Explizite Hyphen-Regel: nur anwenden, wenn das letzte Token einen Bindestrich hat
    last_tok = tokens[-1]
    if "-" in last_tok:
        contact.vorname = " ".join(tokens[:-1])
        contact.nachname = last_tok
    else:
        # 4) Connector-Regel
        low = [t.lower() for t in tokens]
        found = False
        for part in sorted(
            constants.SURNAME_CONNECTORS, key=lambda p: len(p.split()), reverse=True
        ):
            part_toks = part.split()
            for i in range(len(tokens) - len(part_toks) + 1):
                if low[i : i + len(part_toks)] == part_toks:
                    contact.vorname = " ".join(tokens[:i])
                    contact.nachname = " ".join(tokens[i:])
                    found = True
                    break
            if found:
                break
        if not found:
            # 5) Ein-Token-Fall
            if len(tokens) == 1:
                contact.nachname = tokens[0]
            else:
                # 6) Fallback-Split
                vor, nach = _split_first_last(tokens)
                contact.vorname, contact.nachname = vor, nach

    # Title-Casing & Finale Normalisierung
    contact.vorname = unicodedata.normalize("NFC", contact.vorname).title()
    contact.nachname = unicodedata.normalize("NFC", contact.nachname).title()
    return contact
