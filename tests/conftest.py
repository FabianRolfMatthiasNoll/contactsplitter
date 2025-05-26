from domain.contact import Contact
import infrastructure.title_repository
import pytest
from unittest.mock import MagicMock


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

