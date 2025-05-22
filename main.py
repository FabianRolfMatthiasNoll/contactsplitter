import os
import tkinter as tk

from infrastructure.openai_service import OpenAIService
from infrastructure.title_repository import TitleRepository
from infrastructure.name_parser_adapter import DomainNameParser
from infrastructure.ai_adapters import (
    OpenAIGenderDetector,
    OpenAILanguageDetector,
    OpenAIAnredeGenerator,
)
from infrastructure.history_repository import InMemoryHistoryRepository
from application.contact_service import ContactService
from ui.app import KontaktsplitterApp


def main():
    # 1) Konfiguration & Infrastruktur
    api_key = os.getenv("OPENAI_API_KEY", "")
    ai_service = OpenAIService(api_key=api_key)

    # Title-Repository laden
    title_path = os.path.join(os.path.dirname(__file__), "titles.json")
    title_repo = TitleRepository(file_path=title_path)
    title_repo.load()

    # 2) Konkrete Implementierungen
    name_parser = DomainNameParser(title_repo)
    gender_detector = OpenAIGenderDetector(ai_service)
    language_detector = OpenAILanguageDetector(ai_service)
    anrede_generator = OpenAIAnredeGenerator(ai_service)
    history_repo = InMemoryHistoryRepository()

    # 3) Haupt-Service
    contact_service = ContactService(
        name_parser,
        gender_detector,
        language_detector,
        anrede_generator,
        history_repo,
    )

    # 4) UI starten
    root = tk.Tk()
    app = KontaktsplitterApp(root, contact_service, title_repo)
    root.mainloop()


if __name__ == "__main__":
    main()
