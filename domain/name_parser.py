from __future__ import annotations
from typing import List, Tuple
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


def parse_name_to_contact(input_str: str, known_titles: List[str]) -> Contact:
    """
    Zerlegt einen Freitext (z.B. "Frau Dr. Max van den Berg") in ein Contact-Objekt:
      0.5) Erkennung comma-separierter Namen: "Nachname, Vorname" oder mit Titeln/Anrede
      1) Anrede/Saluation (constants.SALUTATIONS)
      2) Titel (known_titles), erkennt führende Titel-Tokens.
      3) Extra-Titel im Rest → contact.inaccuracies
      4) Hyphen-Regel: Nachname ab erstem Bindestrich.
      5) Connector-Regel: Nachname ab Partikel in constants.SURNAME_CONNECTORS.
      6) Ein-Token → Nachname.
      7) Fallback → _split_first_last.
    """
    contact = Contact()
    if not input_str:
        return contact

    # 0.5) Comma-separierte Namen: Vor- und Nachname tauschen, Titel/Anrede korrekt behandeln
    if "," in input_str:
        parts = [p.strip() for p in input_str.split(",", 1)]
        prefix_str, suffix_str = parts[0], parts[1]
        prefix_tokens = prefix_str.replace(",", "").split()
        suffix_tokens = suffix_str.replace(",", "").split()
        if prefix_tokens and suffix_tokens:
            first_clean = prefix_tokens[0].rstrip(".").lower()
            has_salutation = first_clean in constants.SALUTATIONS
            has_title = first_clean in known_titles
            if has_salutation or has_title:
                tokens = prefix_tokens.copy()
                sal_token = None
                # Anrede extrahieren
                if tokens and tokens[0].rstrip(".").lower() in constants.SALUTATIONS:
                    sal_token = tokens.pop(0)
                # Titel extrahieren
                title_tokens_list: List[str] = []
                while tokens and tokens[0].rstrip(".").lower() in known_titles:
                    title_tokens_list.append(tokens.pop(0))
                # Rest ist kompletter Nachname
                last_name_tokens = tokens
                # Neuer Token-Aufbau: [Anrede], [Titel], [Vorname], [Nachname]
                new_tokens: List[str] = []
                if sal_token:
                    new_tokens.append(sal_token)
                new_tokens.extend(title_tokens_list)
                new_tokens.extend(suffix_tokens)
                new_tokens.extend(last_name_tokens)
            else:
                # Kein Salutation oder Titel: Prefix ist kompletter Nachname
                new_tokens = suffix_tokens + prefix_tokens
            new_input_str = " ".join(new_tokens)
            # Einmalig rekursiv ohne Komma parsen
            return parse_name_to_contact(new_input_str, known_titles)

    # 0) Tokenisierung (Kommas entfernen)
    tokens = input_str.replace(",", "").split()

    # 1) Anrede/Saluation
    if tokens:
        key = tokens[0].rstrip(".").lower()
        if key in constants.SALUTATIONS:
            sal = constants.SALUTATIONS[key]
            contact.anrede = tokens.pop(0).rstrip(".")
            contact.geschlecht = sal["gender"]
            contact.sprache = sal["language"]

    # 2) Titel
    titles: List[str] = []
    known_map = {t.strip(".").lower(): t for t in known_titles}
    while tokens:
        clean = tokens[0].rstrip(".").lower()
        if clean in known_map:
            tok = tokens.pop(0)
            titles.append(known_map[clean] + ("." if not tok.endswith(".") else ""))
        else:
            break
    contact.titel = " ".join(titles)

    # 3) Verbleibende Tokens auf weitere Titel prüfen
    remaining = [t.rstrip(".").lower() for t in tokens]
    for tok in remaining:
        if tok in known_map:
            contact.inaccuracies.append(f"Titel im Namen gefunden: „{tok}“")
            break

    if not tokens:
        return contact

    # 4) Explizite Hyphen-Regel
    for idx, tok in enumerate(tokens):
        if "-" in tok:
            contact.vorname = " ".join(tokens[:idx])
            contact.nachname = " ".join(tokens[idx:])
            return contact

    # 5) Connector-Regel
    particles = sorted(
        constants.SURNAME_CONNECTORS,
        key=lambda p: len(p.split()),
        reverse=True,
    )
    low = [t.lower() for t in tokens]
    for part in particles:
        part_toks = part.split()
        for i in range(len(tokens) - len(part_toks) + 1):
            if low[i : i + len(part_toks)] == part_toks:
                contact.vorname = " ".join(tokens[:i])
                contact.nachname = " ".join(tokens[i:])
                return contact

    # 6) Ein-Token-Fall
    if len(tokens) == 1:
        contact.nachname = tokens[0]
        return contact

    # 7) Fallback-Split
    vor, nach = _split_first_last(tokens)
    contact.vorname = vor
    contact.nachname = nach
    return contact
