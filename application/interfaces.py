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
        """Listet alle historisch gespeicherten Kontakte."""
        pass

    @abstractmethod
    def regenerate_briefanrede(self, contact: Contact) -> None:
        """Erzeugt basierend auf aktuellen Feldern eine neue Briefanrede."""
        pass


class ITitleRepository(ABC):
    @abstractmethod
    def load(self) -> None:
        """Lädt die Titeldaten (titles.json)."""
        pass

    @abstractmethod
    def get_titles(self) -> list[str]:
        """Gibt alle bekannten Titel-Token zurück."""
        pass

    @abstractmethod
    def lookup(self, token: str) -> str | None:
        """Liefert die Kurzform zu einem Token oder None."""
        pass

    @abstractmethod
    def add(self, langform: str, kurzform: str) -> bool:
        """Fügt oder aktualisiert einen Titel in titles.json."""
        pass

    @abstractmethod
    def delete(self, langform: str) -> bool:
        """Entfernt einen Titel; Rückgabe True, wenn vorhanden."""
        pass

    @abstractmethod
    def reset_to_defaults(self) -> None:
        """Setzt alle Titel auf die Standardwerte zurück."""
        pass
