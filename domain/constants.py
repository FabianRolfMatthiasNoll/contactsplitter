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
    # — Deutsch —
    "herr": {"gender": "m", "language": "de"},
    "frau": {"gender": "w", "language": "de"},
    # — Englisch —
    "mr": {"gender": "m", "language": "en"},
    "mrs": {"gender": "w", "language": "en"},
    "ms": {"gender": "w", "language": "en"},
    "miss": {"gender": "w", "language": "en"},
    "mx": {"gender": "-", "language": "en"},
    # — Französisch —
    "monsieur": {"gender": "m", "language": "fr"},
    "m": {"gender": "m", "language": "fr"},  # Monsieur (Abk.)
    "madame": {"gender": "w", "language": "fr"},
    "mme": {"gender": "w", "language": "fr"},  # Madame (Abk.)
    "mademoiselle": {"gender": "w", "language": "fr"},
    "mlle": {"gender": "w", "language": "fr"},
    # — Italienisch —
    "signor": {"gender": "m", "language": "it"},
    "sig": {"gender": "m", "language": "it"},  # Sig.
    "signora": {"gender": "w", "language": "it"},
    "sig.ra": {"gender": "w", "language": "it"},  # Sig.ra
    "signorina": {"gender": "w", "language": "it"},
    "sig.na": {"gender": "w", "language": "it"},
    # — Spanisch —
    "señor": {"gender": "m", "language": "es"},
    "senor": {"gender": "m", "language": "es"},
    "sr": {"gender": "m", "language": "es"},
    "señora": {"gender": "w", "language": "es"},
    "senora": {"gender": "w", "language": "es"},
    "sra": {"gender": "w", "language": "es"},
    "señorita": {"gender": "w", "language": "es"},
    "senorita": {"gender": "w", "language": "es"},
    "srta": {"gender": "w", "language": "es"},
    # — Portugiesisch —
    "senhor": {"gender": "m", "language": "pt"},
    "senhora": {"gender": "w", "language": "pt"},
    "senhorita": {"gender": "w", "language": "pt"},
    # — Polnisch —
    "pan": {"gender": "m", "language": "pl"},
    "pani": {"gender": "w", "language": "pl"},
    # — Niederländisch —
    "heer": {"gender": "m", "language": "nl"},
    "mevrouw": {"gender": "w", "language": "nl"},
    # — Schwedisch —
    "fru": {"gender": "w", "language": "sv"},
    "fröken": {"gender": "w", "language": "sv"},
    # — Türkisch —
    "bey": {"gender": "m", "language": "tr"},
    "bay": {"gender": "m", "language": "tr"},
    "hanım": {"gender": "w", "language": "tr"},
    "bayan": {"gender": "w", "language": "tr"},
    # — Indonesisch —
    "pak": {"gender": "m", "language": "id"},
    "ibu": {"gender": "w", "language": "id"},
}

# Partikel, bei denen der Nachname **ab** dem Partikel beginnt
SURNAME_CONNECTORS: set[str] = {
    # bisherige europäische Partikel…
    "von",
    "zu",
    "zur",
    "zum",
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
    "della",
    "dello",
    "degli",
    "al",
    "bin",
    "ibn",
    "bint",
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
    "diplomingenieur": "Dipl. Ing.",
    # — Deutsch: Adelstitel —
    "freiherr": "Frhr.",
    "reichsfreiherr": "RFrhr.",
    "baron": "Baron",
    "graf": "Gräf.",
    "reichsgraf": "S. R. Graf",
    "reichsgraf": "S. R. Gräfin",
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
