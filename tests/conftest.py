from domain.contact import Contact
import infrastructure.title_repository
import pytest
from unittest.mock import MagicMock
import os
from infrastructure.openai_service import OpenAIService
from infrastructure.title_repository import TitleRepository
from infrastructure.name_parser_adapter import DomainNameParser
from infrastructure.ai_adapters import OpenAIGenderDetector, OpenAILanguageDetector, OpenAIAnredeGenerator
from infrastructure.history_repository import InMemoryHistoryRepository
from application.contact_service import ContactService

@pytest.fixture
def mock_title_repository(monkeypatch):
    mock_repo = MagicMock()
    mock_repo.load.return_value = None
    mock_repo.get_titles.return_value = ["doktor", "professor", "graf", "dr. rer. nat"]

    def lookup(token: str):
        t = token.rstrip(".").lower()
        if t in ("dr", "doktor"):
            return "Dr."
        if t in ("dr. rer. nat"):
            return "Dr. Rer. Nat."
        if t in ("prof", "professor"):
            return "Prof."
        if t == "graf":
            return "Graf"
        return None
    
    mock_repo.lookup.side_effect = lookup
    mock_repo.add.return_value = True
    mock_repo.delete.return_value = True
    mock_repo.reset_to_defaults.return_value = None

    monkeypatch.setattr(infrastructure.title_repository, 'TitleRepository', mock_repo)
    return mock_repo

@pytest.fixture
def contact_service():
    ai_service = OpenAIService()

    title_repo = TitleRepository(file_path="titles.json")
    title_repo.load()

    name_parser = DomainNameParser(title_repo)
    gender_detector = OpenAIGenderDetector(ai_service)
    language_detector = OpenAILanguageDetector(ai_service)
    anrede_generator = OpenAIAnredeGenerator(ai_service)
    history_repo = InMemoryHistoryRepository()

    contact_service = ContactService(
        name_parser,
        gender_detector,
        language_detector,
        anrede_generator,
        history_repo,
    )

    return contact_service
