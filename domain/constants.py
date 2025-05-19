"""
Konstanten für die Namensparsing-Logik.

SALUTATIONS:
    Mapping von Anrede-Token (klein, ohne Punkt) auf ein Dict mit:
      - gender: "m" für männlich, "w" für weiblich, "-" für unbekannt
      - language: Sprachcode, z. B. "de" oder "en"

PREPEND_PARTICLES:
    Mengen von mehr- oder einwortigen Partikeln (z. B. "von", "von der"),
    bei denen zusätzlich **ein Token vor** der Partikel zur Nachnameinheit gehört.
    Beispiel: "Noll von Dettelberg" → Nachname: "Noll von Dettelberg".

NO_PREPEND_PARTICLES:
    Mengen von Partikeln (z. B. "van", "de", "del"), bei denen der Nachname
    **genau ab** der Partikel beginnt. Beispiel: "Vincent van Gogh"
    → Nachname: "van Gogh".

SURNAME_CONNECTORS:
    Vereinigung aus PREPEND_PARTICLES und NO_PREPEND_PARTICLES.
    Wird als Fallback in `_split_first_last` verwendet, um längere
    toponymische Zusätze rückwärts an den Nachnamen zu koppeln.

DEFAULT_TITLES:
    Erweiterte Titeldatenbank (Token → kanonische Kurzform), die
    akademische sowie Adelstitel in Deutsch, Niederländisch, Französisch,
    Spanisch/Portugiesisch und Italienisch abdeckt.
"""

from __future__ import annotations

# Known salutation tokens (Anreden) mapped to gender and language.
# Keys are normalized to lowercase (without punctuation).
SALUTATIONS: dict[str, dict[str, str]] = {
    # German
    "herr": {"gender": "m", "language": "de"},
    "frau": {"gender": "w", "language": "de"},
    # English
    "mr": {"gender": "m", "language": "en"},
    "mrs": {"gender": "w", "language": "en"},
    "ms": {"gender": "w", "language": "en"},
    "miss": {"gender": "w", "language": "en"},
    # French
    "m": {"gender": "m", "language": "fr"},  # Monsieur (abbrev)
    "monsieur": {"gender": "m", "language": "fr"},
    "mme": {"gender": "w", "language": "fr"},  # Madame (abbrev)
    "madame": {"gender": "w", "language": "fr"},
    # Italian
    "signor": {"gender": "m", "language": "it"},
    "signora": {"gender": "w", "language": "it"},
    "sig": {"gender": "m", "language": "it"},  # Sig. abbreviation for Signor
    "sig.ra": {"gender": "w", "language": "it"},  # Sig.ra abbreviation for Signora
    # Spanish
    "señor": {"gender": "m", "language": "es"},  # "Señor"
    "senor": {"gender": "m", "language": "es"},  # allow no accent
    "señora": {"gender": "w", "language": "es"},  # "Señora"
    "senora": {"gender": "w", "language": "es"},  # allow no accent
    "sr": {"gender": "m", "language": "es"},  # Sr. abbreviation for Señor
    "sra": {"gender": "w", "language": "es"},  # Sra. abbreviation for Señora
}

# Partikel, bei denen der Nachname **ab** dem Partikel beginnt
SURNAME_CONNECTORS = {
    "von",
    "zu",
    "zur",
    "zum",
    "von der",
    "von dem",
    "von und zu",
    "vom",
    "van",
    "van de",
    "van der",
    "van den",
    "vande",
    "vanden",
    "vander",
    "de",
    "de la",
    "du",
    "des",
    "del",
    "de los",
    "de las",
    "da",
    "do",
    "dos",
    "das",
    "di",
    "del",
    "della",
    "dello",
    "degli",
}

DEFAULT_TITLES = {
    # — Deutsch: akademische Titel —
    "doktor": "Dr.",
    "dr": "Dr.",
    "professor": "Prof.",
    "prof": "Prof.",
    "honorarprofessor": "Hon.-Prof.",
    "privatdozent": "Priv.-Doz.",
    "juniorprofessor": "Jun.-Prof.",
    "diplomingenieur": "Dipl.-Ing.",
    # — Deutsch: Adelstitel —
    "freiherr": "Frhr.",
    "reichsfreiherr": "RFrhr.",
    "baron": "Baron",
    "graf": "Gräf.",
    "reichsgraf": "RGräf.",
    "fürst": "Fürst.",
    "herzog": "Herz.",
    "prinz": "Prinz",
    "landgraf": "Lgr.",
    "markgraf": "Mgr.",
    "pfalzgraf": "Pfg.",
    # — Niederländisch —
    "doctor": "Dr.",
    "ingenieur": "Ir.",
    "ir": "Ir.",
    "jonkheer": "Jhr.",
    "ridder": "Rdr.",
    # — Französisch —
    "docteur": "Dr.",
    "professeur": "Prof.",
    "comte": "Cte.",
    "duc": "Duc",
    "prince": "Pr.",
    "chevalier": "Ch.",
    # — Spanisch/Portugiesisch —
    "profesor": "Prof.",
    "conde": "Cde.",
    "duque": "Duce.",
    "principe": "Pr.",
    "princesa": "Pr.",
    "marques": "Marq.",
    "marquesa": "Marq.",
    "vizconde": "Vizc.",
    # — Italienisch —
    "dottore": "Dott.",
    "professore": "Prof.",
    "barone": "Bar.",
    "conte": "Conte",
    "duca": "Duca",
    "principe": "Prin.",
}
