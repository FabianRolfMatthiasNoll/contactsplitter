# application/contact_service.py

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
        # Ensure titles are loaded
        self.title_repo.load()
        logger.info(f"Loaded {len(self.title_repo.get_titles())} titles.")

    def parse_input_to_contact(self, input_str: str) -> Contact:
        """
        Parse a raw input string and enrich it into a Contact object,
        without modifying the in-memory history.
        """
        if input_str is None:
            input_str = ""
        input_str = input_str.strip()

        # Validation
        if input_str == "" or len(input_str) > 255:
            logger.warning("Invalid input string (empty or too long).")
            contact = Contact()
            contact.needs_review = True
            return contact

        # 1) Grundlegendes Parsen
        contact = name_parser.parse_name_to_contact(
            input_str, self.title_repo.get_titles()
        )

        if contact.titel:
            normalized = []
            for tok in contact.titel.split():
                # entferne Punkt-Endung, falls vorhanden
                key = tok.rstrip(".").lower()
                short = self.title_repo.lookup(key)
                normalized.append(short or tok)
            contact.titel = " ".join(normalized)

        # 2) Geschlecht via AI, falls nicht aus Anrede ermittelt
        if contact.geschlecht == "-" and contact.vorname:
            try:
                contact.geschlecht = self.ai_service.detect_gender(
                    contact.vorname + " " + contact.nachname
                )
            except Exception as e:
                logger.error(f"Gender detection via AI failed: {e}")

        # 3) Sprache via AI, falls nicht aus Anrede ermittelt
        if not contact.sprache:
            name_for_lang = f"{contact.vorname} {contact.nachname}".strip()
            if name_for_lang:
                try:
                    detected = self.ai_service.detect_language(name_for_lang)
                except Exception as e:
                    logger.error(f"Language detection via AI failed: {e}")
                    detected = ""
                contact.sprache = detected or ""

        #    Falls keine Anrede im Input, aber nun Geschlecht+Sprache bekannt,
        #    wählen wir aus constants.SALUTATIONS die passende Kombination.
        if not contact.anrede and contact.geschlecht in ("m", "w") and contact.sprache:
            for key, val in constants.SALUTATIONS.items():
                if (
                    val["gender"] == contact.geschlecht
                    and val["language"] == contact.sprache
                ):
                    # Key ist z.B. "herr" oder "frau" oder "mr"
                    contact.anrede = key.capitalize()
                    break

        # 4) Briefanrede generieren
        contact.briefanrede = self.ai_service.generate_briefanrede(contact)

        # 5) Review-Flag setzen
        if (
            contact.geschlecht == "-"
            or contact.sprache == ""
            or not contact.vorname
            or not contact.nachname
        ):
            contact.needs_review = True
        else:
            contact.needs_review = False

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
        # Review-Flag ggf. neu setzen
        if (
            contact.geschlecht == "-"
            or contact.sprache == ""
            or not contact.vorname
            or not contact.nachname
        ):
            contact.needs_review = True
        else:
            contact.needs_review = False

    def save_new_title(self, title: str, shortform: str) -> bool:
        """
        Speichert einen neuen Titel in die Repository (persistiert in titles.json).
        """
        return self.title_repo.add(title, shortform)
