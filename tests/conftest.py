from domain.contact import Contact
import infrastructure.title_repository
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_title_repository(monkeypatch):
    mock_repo = MagicMock()
    mock_repo.load.return_value = None
    mock_repo.get_titles.return_value = ["doktor", "professor", "graf"]
    mock_repo.lookup.side_effect = lambda title: (
        "doktor" if title in ["Dr.", "Doktor"] else
        "professor" if title in ["Prof.", "Professor"] else
        "graf" if title == "Graf" else
        None
    )
    mock_repo.add.return_value = True
    mock_repo.delete.return_value = True
    mock_repo.reset_to_defaults.return_value = None

    monkeypatch.setattr(infrastructure.title_repository, 'TitleRepository', mock_repo)
    return mock_repo

