# main.py

import os
import tkinter as tk

from infrastructure.openai_service import OpenAIService
from infrastructure.title_repository import JsonTitleRepository
from application.interfaces import (
    SimpleNameParser,
    OpenAIGenderDetector,
    OpenAILanguageDetector,
    OpenAIAnredeGenerator,
    InMemoryHistoryRepository,
)
from application.contact_service import ContactService
from ui.kontaktsplitter_app import KontaktsplitterApp

def main():
    # 1) Konfiguration & Infrastruktur
    api_key = os.getenv("OPENAI_API_KEY", "")
    ai_service = OpenAIService(api_key=api_key)
    title_repo = JsonTitleRepository(path="titles.json")

    # 2) Konkrete Implementierungen
    name_parser       = SimpleNameParser()
    gender_detector   = OpenAIGenderDetector(ai_service)
    language_detector = OpenAILanguageDetector(ai_service)
    anrede_generator  = OpenAIAnredeGenerator(ai_service, title_repo)
    history_repo      = InMemoryHistoryRepository()

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
