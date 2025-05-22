from abc import ABC, abstractmethod
from typing import List
from domain.contact import Contact


class INameParser(ABC):
    @abstractmethod
    def parse(self, raw_input: str) -> Contact:
        """Zerlegt den Roh-String in ein Contact-Objekt."""
        pass


class IGenderDetector(ABC):
    @abstractmethod
    def detect(self, contact: Contact) -> str:
        """Ermittelt das Geschlecht ('m', 'w' oder '-')."""
        pass


class ILanguageDetector(ABC):
    @abstractmethod
    def detect(self, contact: Contact) -> str:
        """Ermittelt den Sprachcode ('de', 'en', ...)."""
        pass


class IAnredeGenerator(ABC):
    @abstractmethod
    def generate(self, contact: Contact) -> str:
        """Erzeugt die formelle Briefanrede."""
        pass


class IHistoryRepository(ABC):
    @abstractmethod
    def save(self, contact: Contact) -> None:
        """Speichert einen Kontakt dauerhaft (z. B. in DB oder In-Memory)."""
        pass

    @abstractmethod
    def list(self) -> List[Contact]:
        """Gibt alle gespeicherten Kontakte zurück."""
        pass


class IContactService(ABC):
    @abstractmethod
    def process(self, raw_input: str) -> Contact:
        """Zerlegt und erkennt alle Felder eines Kontakts."""
        pass

    @abstractmethod
    def save_contact(self, contact: Contact) -> None:
        """Legt den Kontakt in der Historie ab."""
        pass

    @abstractmethod
    def get_history(self) -> List[Contact]:
        """Liistet alle historisch gespeicherten Kontakte."""
        pass

    @abstractmethod
    def regenerate_briefanrede(self, contact: Contact) -> None:
        """Erzeugt basierend auf aktuellen Feldern eine neue Briefanrede."""
        pass
