from infrastructure.title_repository import TitleRepository
from unittest.mock import patch
import domain.constants


def test_create_repo():
    repo = TitleRepository("tests/data/titles.json")
    assert (repo)
    assert (repo.get_titles() == [])


def test_load_repo_from_file():
    repo = TitleRepository("tests/data/titles.json")
    assert (repo)
    repo.load()
    assert (repo.get_titles() == ['doktor', 'dr', 'professor', 'prof'])


def test_load_repo_from_non_existing_file(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.get_titles() == ['the_only_key'])


def test_repo_lookup_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("the_only_key") == "the_only_value")


def test_repo_lookup_non_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("invalid_key") == None)


def test_repo_add_non_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("added_key") == None)
    assert (repo.add("added_key", "added_value") == True)
    assert (repo.lookup("added_key") == "added_value")


def test_repo_add_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("the_only_key") == "the_only_value")
    assert (repo.add("the_only_key", "updated_value") == True)
    assert (repo.lookup("the_only_key") == "updated_value")


def test_repo_add_same_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("the_only_key") == "the_only_value")
    assert (repo.add("the_only_key", "the_only_value") == False)
    assert (repo.lookup("the_only_key") == "the_only_value")


def test_repo_delete_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("the_only_key") == "the_only_value")
    assert (repo.delete("the_only_key") == True)
    assert (repo.lookup("the_only_key") == None)


def test_repo_delete_non_existing_title(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.delete("invalid_key") == False)


def test_repo_reset_to_default(monkeypatch, tmp_path):
    monkeypatch.setattr('infrastructure.title_repository.DEFAULT_TITLES', {"the_only_key": "the_only_value"})
    non_existent_file = str(tmp_path / "nonexistent.json")

    repo = TitleRepository(non_existent_file)
    assert (repo)
    repo.load()
    assert (repo.lookup("added_key") == None)
    assert (repo.add("added_key", "added_value") == True)
    assert (repo.lookup("added_key") == "added_value")
    assert (repo.reset_to_defaults() == None)
    assert (repo.lookup("added key") == None)

