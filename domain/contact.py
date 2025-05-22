from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Union


@dataclass
class Contact:
    """Repräsentiert einen geparsten Kontakt."""

    anrede: str = ""
    titel: str = ""
    vorname: str = ""
    nachname: str = ""
    geschlecht: str = "-"  # 'm', 'w' oder '-'
    sprache: str = ""
    briefanrede: str = ""
    needs_review: bool = False
    inaccuracies: List[str] = field(default_factory=list)
    review_fields: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.geschlecht:
            self.geschlecht = "-"
        if self.inaccuracies or self.review_fields:
            self.needs_review = True

    def to_dict(self) -> Dict[str, Union[str, bool, List[str]]]:
        return {
            "anrede": self.anrede,
            "titel": self.titel,
            "vorname": self.vorname,
            "nachname": self.nachname,
            "geschlecht": self.geschlecht,
            "sprache": self.sprache,
            "briefanrede": self.briefanrede,
            "needs_review": self.needs_review,
            "inaccuracies": self.inaccuracies,
            "review_fields": self.review_fields,
        }

    def __str__(self) -> str:
        base = (
            f"Contact(anrede={self.anrede!r}, titel={self.titel!r}, "
            f"vorname={self.vorname!r}, nachname={self.nachname!r}, "
            f"geschlecht={self.geschlecht!r}, sprache={self.sprache!r}, "
            f"briefanrede={self.briefanrede!r}, needs_review={self.needs_review}"
        )
        if self.inaccuracies:
            base += f", inaccuracies={self.inaccuracies!r}"
        if self.review_fields:
            base += f", review_fields={self.review_fields!r}"
        base += ")"
        return base
