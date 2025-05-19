# domain/name_parser.py

"""
Name parsing logic according to defined rules (siehe Spezifikation § 3),
mit folgender Anpassung:
- Automatische Hyphenisierung bei Mehr-Wort-Nachnamen entfällt.
- Explizit eingegebene Bindestriche bleiben erhalten.
- Ab dem ersten Connector-Token ("von", "van" …) gilt der Rest als Nachname.
  Nice-to-have: Werden zwei aufeinanderfolgende Eigennamen ohne Connector
  eingegeben, werden diese zu einem Bindestrich-Nachnamen kombiniert.
"""

from __future__ import annotations
from typing import List, Tuple
from domain.contact import Contact
from domain import constants


def _split_first_last(name_tokens: List[str]) -> Tuple[str, str]:
    """
    Hilfs-Split: Letztes Token(-Block) = Nachname (inkl. Connectoren rückwärts),
    Rest = Vorname.
    """
    if not name_tokens:
        return "", ""
    idx_last = len(name_tokens) - 1
    last = [name_tokens[idx_last]]
    j = idx_last - 1
    while j >= 0:
        t = name_tokens[j].rstrip(".").lower()
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
    Parse a free-text salutation string (z. B. "Herr Dr. Max von Müller") in Contact.
    Ablauf:
      1) Komma-Notation ("Müller, Max") erkennen
      2) Anrede (constants.SALUTATIONS)
      3) Titel (known_titles)
      4) Nachname ab erstem Connector ("von", "van" …)
      5) Fallback-Split (_split_first_last)
      Nice-to-have: Wenn die letzten beiden Tokens Großbuchstaben-Anfang
      ohne Connector sind, werden sie zu einem Bindestrich-Namen vereint.
    """
    contact = Contact()
    if not input_str:
        return contact

    text = input_str.strip()
    if text == "" or len(text) > 255:
        contact.needs_review = True
        return contact

    # 1) Komma-Notation
    if "," in text:
        left, right = [p.strip() for p in text.split(",", 1)]
        tl = left.split()
        tr = right.split()
        if tl:
            contact.nachname = tl[-1]
            contact.titel = " ".join(tl[:-1])
        contact.vorname = " ".join(tr)
        return contact

    tokens = text.split()

    # 2) Anrede
    if tokens:
        key = tokens[0].rstrip(".").lower()
        if key in constants.SALUTATIONS:
            sal = constants.SALUTATIONS[key]
            contact.anrede = tokens[0].rstrip(".")
            contact.geschlecht = sal["gender"]
            contact.sprache = sal["language"]
            tokens = tokens[1:]

    # 3) Titel
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

    # 4) Connector-Regel
    for idx, tok in enumerate(tokens):
        if tok.rstrip(".").lower() in constants.SURNAME_CONNECTORS:
            # ab idx = gesamter Nachname
            vor = tokens[:idx]
            surname = tokens[idx:]
            # nice-to-have: letzte zwei ohne Connector hyphenieren
            if len(surname) >= 2:
                a, b = surname[-2], surname[-1]
                if (
                    all("-" not in x for x in (a, b))
                    and a[0].isupper()
                    and b[0].isupper()
                ):
                    surname[-2] = f"{a}-{b}"
                    surname.pop()
            contact.vorname = " ".join(vor)
            contact.nachname = " ".join(surname)
            return contact

    # 5a) Ein-Token bleibt = Nachname
    if len(tokens) == 1:
        contact.nachname = tokens[0]
        return contact

    # 5b) Fallback
    vor, nach = _split_first_last(tokens)
    contact.vorname = vor
    contact.nachname = nach
    return contact
