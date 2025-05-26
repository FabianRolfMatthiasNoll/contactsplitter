from typing import List
from application.interfaces import (
    INameParser,
    IGenderDetector,
    ILanguageDetector,
    IAnredeGenerator,
    IHistoryRepository,
    IContactService,
)
from domain.contact import Contact


class ContactService(IContactService):
    def __init__(
        self,
        name_parser: INameParser,
        gender_detector: IGenderDetector,
        language_detector: ILanguageDetector,
        anrede_generator: IAnredeGenerator,
        history_repo: IHistoryRepository,
        history_size: int = 10,
    ):
        self.name_parser = name_parser
        self.gender_detector = gender_detector
        self.language_detector = language_detector
        self.anrede_generator = anrede_generator
        self.history_repo = history_repo
        self.history_size = history_size

    def process(self, raw_input: str) -> Contact:
        # 1) Parsing
        contact = self.name_parser.parse(raw_input)

        # 2) Geschlecht
        if contact.geschlecht == "-" and contact.vorname:
            contact.geschlecht = self.gender_detector.detect(contact)

        # 3) Sprache
        if not contact.sprache:
            contact.sprache = self.language_detector.detect(contact)

        # 4) Briefanrede
        if not contact.briefanrede:
            contact.briefanrede = self.anrede_generator.generate(contact)

        # 5) Feld-Validierung
        contact.review_fields.clear()
        if not contact.vorname:
            contact.inaccuracies.append("Vorname fehlt")
            contact.review_fields.append("vorname")
            contact.needs_review = True
        if not contact.nachname:
            contact.inaccuracies.append("Nachname fehlt")
            contact.review_fields.append("nachname")
            contact.needs_review = True

        return contact

    def save_contact(self, contact: Contact) -> None:
        self.history_repo.save(contact)
        # Trimm auf max. history_size
        hist = self.history_repo.list()
        if len(hist) > self.history_size:
            # älteste Einträge entfernen
            excess = len(hist) - self.history_size
            for _ in range(excess):
                hist.pop(0)

    def get_history(self) -> List[Contact]:
        return self.history_repo.list()

    def regenerate_briefanrede(self, contact: Contact) -> None:
        contact.briefanrede = self.anrede_generator.generate(contact)
