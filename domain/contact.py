"""Domain model for contact information (anrede, name parts, etc.)."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Contact:
    """Data class representing a parsed contact with various fields."""

    anrede: str = ""  # salutation (e.g. "Herr", "Mrs")
    titel: str = ""  # academic or honorific titles (all titles in input order)
    vorname: str = ""  # first name(s)
    nachname: str = ""  # last name
    geschlecht: str = "-"  # gender: "m", "w", or "-" if unknown
    sprache: str = ""  # language code (ISO-639-1, e.g. "de", "en")
    briefanrede: str = ""  # letter salutation line
    needs_review: bool = False  # indicates ambiguous or uncertain parsing

    def __post_init__(self):
        # Ensure fields have the correct types or normalized values if needed
        if not self.geschlecht:
            self.geschlecht = "-"
        if not self.sprache:
            self.sprache = ""

    def to_dict(self) -> dict[str, str | bool]:
        """Convert Contact to dictionary (for serialization or display)."""
        return {
            "anrede": self.anrede,
            "titel": self.titel,
            "vorname": self.vorname,
            "nachname": self.nachname,
            "geschlecht": self.geschlecht,
            "sprache": self.sprache,
            "briefanrede": self.briefanrede,
            "needs_review": self.needs_review,
        }

    def __str__(self) -> str:
        """String representation for debugging (not necessarily for UI)."""
        return (
            f"Contact(anrede={self.anrede!r}, titel={self.titel!r}, "
            f"vorname={self.vorname!r}, nachname={self.nachname!r}, "
            f"geschlecht={self.geschlecht!r}, sprache={self.sprache!r}, "
            f"briefanrede={self.briefanrede!r}, needs_review={self.needs_review})"
        )
