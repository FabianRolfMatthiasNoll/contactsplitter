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
        if j < len(name_tokens) - 1:
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
      1) Anrede/Saluation (constants.SALUTATIONS)
      2) Titel (known_titles)
      3) Explizite Hyphen-Regel: ab erstem Bindestrich → Nachname.
      4) Partikel-Regel:
         - Sortiere alle Partikel (PREPEND + NO_PREPEND) nach Tokenlänge absteigend.
         - Suche Vorkommen; entscheide start-Index je nach Set.
      5) Ein-Token → Nachname.
      6) Fallback → _split_first_last.
    """
    contact = Contact()
    if not input_str:
        return contact

    # 0) Tokenisierung
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
            titles.append(
                known_map[clean] + ("." if not tokens[0].endswith(".") else "")
            )
            tokens.pop(0)
        else:
            break
    contact.titel = " ".join(titles)

    if not tokens:
        return contact

    # 3) Explizite Hyphen-Regel
    for idx, tok in enumerate(tokens):
        if "-" in tok:
            contact.vorname = " ".join(tokens[:idx])
            contact.nachname = " ".join(tokens[idx:])
            return contact

    # 4) Partikel-Regel (mehrwortige zuerst)
    particles = sorted(
        list(constants.PREPEND_PARTICLES | constants.NO_PREPEND_PARTICLES),
        key=lambda p: len(p.split()),
        reverse=True,
    )
    low_tokens = [t.lower() for t in tokens]
    for part in particles:
        part_toks = part.split()
        for i in range(len(tokens) - len(part_toks) + 1):
            if low_tokens[i : i + len(part_toks)] == part_toks:
                # ggf. ein Token voranstellen
                if part in constants.PREPEND_PARTICLES and i > 0:
                    start = i - 1
                else:
                    start = i
                contact.vorname = " ".join(tokens[:start])
                contact.nachname = " ".join(tokens[start:])
                return contact

    # 5) Ein-Token-Fall
    if len(tokens) == 1:
        contact.nachname = tokens[0]
        return contact

    # 6) Fallback-Split
    vor, nach = _split_first_last(tokens)
    contact.vorname = vor
    contact.nachname = nach
    return contact
