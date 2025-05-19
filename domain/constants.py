"""Constants and configuration for the kontaktsplitter domain logic."""

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

# Known surname connector tokens that should be considered part of last name if present.
# Multi-word connectors (e.g., "van der") are handled by checking each token and combining if sequential connectors.
SURNAME_CONNECTORS: set[str] = {
    "von",
    "van",
    "van der",
    "de",
    "da",
    "del",
    "der",
    "di",
    "do",
}
