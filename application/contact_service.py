"""Application service for processing contact input through parsing and detection steps."""

import logging
from domain import constants, name_parser
from domain.contact import Contact
from infrastructure.title_repository import TitleRepository
from infrastructure.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(
        self,
        title_repo: TitleRepository,
        ai_service: OpenAIService,
        history_size: int = 10,
    ):
        """
        Initialize ContactService with a title repository and an OpenAI service for detection.
        history_size defines how many contacts to keep in history.
        """
        self.title_repo = title_repo
        self.ai_service = ai_service
        self.history_size = history_size
        self.history: list[Contact] = []
        self.title_repo.load()
        logger.info(f"Loaded {len(self.title_repo.get_titles())} titles.")

    def parse_input_to_contact(self, input_str: str) -> Contact:
        """
        Parse a raw input string and enrich it into a Contact object,
        ohne die Historie zu verändern.
        Markiert nur die Felder in review_fields, die leer sind oder ungenau erkannt wurden.
        """
        contact = Contact()

        # 0) Grund-Validierung
        if not input_str or len(input_str) > 255:
            msg = "Eingabe ungültig (leer oder >255 Zeichen)"
            contact.inaccuracies.append(msg)
            # Vorname & Nachname fehlen auf jeden Fall
            contact.review_fields.extend(["vorname", "nachname"])
            return contact

        input_str = input_str.strip()

        # 1) Name parsen
        contact = name_parser.parse_name_to_contact(
            input_str, self.title_repo.get_titles()
        )

        # 2) Titel-Normalisierung
        if contact.titel:
            normalized = []
            for tok in contact.titel.split():
                key = tok.rstrip(".").lower()
                short = self.title_repo.lookup(key)
                normalized.append(short or tok)
            contact.titel = " ".join(normalized)

        # 3) AI: Geschlecht falls nötig
        if contact.geschlecht == "-" and contact.vorname:
            try:
                contact.geschlecht = self.ai_service.detect_gender(
                    f"{contact.vorname} {contact.nachname}".strip()
                )
            except Exception as e:
                logger.error(f"Gender detection via AI failed: {e}")

        # 4) AI: Sprache falls nötig
        if not contact.sprache:
            try:
                contact.sprache = self.ai_service.detect_language(
                    f"{contact.vorname} {contact.nachname}".strip()
                )
            except Exception as e:
                logger.error(f"Language detection via AI failed: {e}")

        # 5) Fallback-Anrede
        if not contact.anrede and contact.geschlecht in ("m", "w") and contact.sprache:
            for key, val in constants.SALUTATIONS.items():
                if (
                    val["gender"] == contact.geschlecht
                    and val["language"] == contact.sprache
                ):
                    contact.anrede = key.capitalize()
                    break

        # 6) Briefanrede
        contact.briefanrede = self.ai_service.generate_briefanrede(contact)

        # 7) Feld-Validierung: nur echt leere/ungenaue Felder markieren
        contact.review_fields.clear()
        # Pflichtfelder prüfen
        for fld, name in [
            ("vorname", "Vorname"),
            ("nachname", "Nachname"),
        ]:
            if not getattr(contact, fld):
                contact.inaccuracies.append(f"{name} fehlt")
                contact.review_fields.append(fld)
        # Ungenauigkeiten aus name_parser (z.B. weiterer Titel im Rest)
        if any("Titel im Namen gefunden" in note for note in contact.inaccuracies):
            if "titel" not in contact.review_fields:
                contact.review_fields.append("titel")

        return contact

    def process_input(self, input_str: str) -> Contact:
        """
        Entry point für Parsing & Erkennung. Liefert ein Contact-Objekt,
        fügt es aber nicht automatisch in die Historie ein.
        """
        return self.parse_input_to_contact(input_str)

    def add_to_history(self, contact: Contact) -> None:
        """
        Fügt einen Contact manuell in die In-Memory-Historie ein
        und trimmt sie auf self.history_size.
        """
        self._add_to_history(contact)

    def _add_to_history(self, contact: Contact):
        """Interne Hilfsmethode für die Historien-Verwaltung."""
        self.history.append(contact)
        if len(self.history) > self.history_size:
            self.history.pop(0)
        logger.info(f"Added contact to history (size now {len(self.history)}).")

    def regenerate_briefanrede(self, contact: Contact) -> None:
        """
        Regenerate die Briefanrede (z.B. nach manuellen Feldänderungen).
        """
        contact.briefanrede = self.ai_service.generate_briefanrede(contact)
        # keine weiteren Validierungen hier nötig

    def save_new_title(self, title: str, shortform: str) -> bool:
        """
        Speichert einen neuen Titel in die Repository (persistiert in titles.json).
        """
        return self.title_repo.add(title, shortform)
