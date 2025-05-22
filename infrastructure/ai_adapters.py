from application.interfaces import IGenderDetector, ILanguageDetector, IAnredeGenerator
from domain.contact import Contact
from infrastructure.openai_service import OpenAIService


class OpenAIGenderDetector(IGenderDetector):
    def __init__(self, ai_service: OpenAIService):
        self.ai = ai_service

    def detect(self, contact: Contact) -> str:
        name = f"{contact.vorname} {contact.nachname}".strip()
        return self.ai.detect_gender(name)


class OpenAILanguageDetector(ILanguageDetector):
    def __init__(self, ai_service: OpenAIService):
        self.ai = ai_service

    def detect(self, contact: Contact) -> str:
        name = f"{contact.vorname} {contact.nachname}".strip()
        return self.ai.detect_language(name)


class OpenAIAnredeGenerator(IAnredeGenerator):
    def __init__(self, ai_service: OpenAIService):
        self.ai = ai_service

    def generate(self, contact: Contact) -> str:
        return self.ai.generate_briefanrede(contact)
