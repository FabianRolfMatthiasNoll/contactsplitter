"""Application service for processing contact input through parsing and detection steps."""

import logging
from domain import name_parser
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

    def process_input(self, input_str: str) -> Contact:
        """
        Process a raw input string to parse and enrich it into a Contact object.
        Performs parsing, gender/language detection, briefanrede generation, and sets needs_review if necessary.
        """
        if input_str is None:
            input_str = ""
        input_str = input_str.strip()
        # Validation
        if input_str == "" or len(input_str) > 255:
            logger.warning("Invalid input string (empty or too long).")
            # Return an empty contact indicating invalid input
            contact = Contact()
            contact.needs_review = True
            return contact
        # Parse input into basic fields
        contact = name_parser.parse_name_to_contact(
            input_str, self.title_repo.get_titles()
        )
        # If gender not determined via anrede, try via AI on first name
        if contact.geschlecht == "-" and contact.vorname:
            try:
                contact.geschlecht = self.ai_service.detect_gender(
                    contact.vorname.split()[0]
                )
            except Exception as e:
                logger.error(f"Gender detection via AI failed: {e}")
        # If language not determined via salutation, try via AI on name
        if not contact.sprache or contact.sprache == "":
            name_for_lang = f"{contact.vorname} {contact.nachname}".strip()
            if name_for_lang:
                try:
                    detected = self.ai_service.detect_language(name_for_lang)
                except Exception as e:
                    logger.error(f"Language detection via AI failed: {e}")
                    detected = ""
                contact.sprache = detected if detected else ""
        # Generate briefanrede
        contact.briefanrede = self.ai_service.generate_briefanrede(contact)
        # Determine if needs_review should be set
        if (
            contact.geschlecht == "-"
            or contact.sprache == ""
            or not contact.vorname
            or not contact.nachname
        ):
            # If any key information is missing or ambiguous, flag for review
            contact.needs_review = True
        else:
            contact.needs_review = False
        # Add to history
        self._add_to_history(contact)
        return contact

    def _add_to_history(self, contact: Contact):
        """Add a contact to history (in-memory). Trims history if exceeding size."""
        self.history.append(contact)
        if len(self.history) > self.history_size:
            # remove oldest
            self.history.pop(0)
        logger.info(f"Added contact to history (size now {len(self.history)}).")

    def regenerate_briefanrede(self, contact: Contact) -> None:
        """
        Regenerate the briefanrede for a given Contact (e.g., after manual field changes).
        """
        contact.briefanrede = self.ai_service.generate_briefanrede(contact)
        # Re-evaluate review flag if needed
        if (
            contact.geschlecht == "-"
            or contact.sprache == ""
            or not contact.vorname
            or not contact.nachname
        ):
            contact.needs_review = True
        else:
            contact.needs_review = False

    def save_new_title(self, title: str) -> bool:
        """
        Save a new title to the title repository (and persist it).
        Returns True if added, False if it was already known or invalid.
        """
        return self.title_repo.add(title)
