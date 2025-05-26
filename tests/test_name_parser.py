from domain.contact import Contact
from domain.name_parser import parse_name_to_contact
from unittest.mock import patch

def test_parse_empy(mock_title_repository):
    contact = Contact()
    assert (parse_name_to_contact("", mock_title_repository) == contact)


def test_parse_single_letter(mock_title_repository):
    contact = Contact()
    contact.nachname = "A"
    assert (parse_name_to_contact("A", mock_title_repository) == contact)


def test_parse_last_name(mock_title_repository):
    contact = Contact()
    contact.vorname = "Benjamin"
    contact.nachname = "Henrisson"
    assert (parse_name_to_contact("benjamin henrisson", mock_title_repository) == contact)


def test_parse_name_capitalisation(mock_title_repository):
    contact = Contact()
    contact.nachname = "Henrisson"
    assert (parse_name_to_contact("Henrisson", mock_title_repository) == contact)


def test_parse_last_name_with_hyphen(mock_title_repository):
    contact = Contact()
    contact.nachname = "Henrisson-Ford"
    assert (parse_name_to_contact("Henrisson-Ford", mock_title_repository) == contact)


def test_parse_first_and_last_name(mock_title_repository):
    contact = Contact()
    contact.vorname = "Henri"
    contact.nachname = "Henrisson"
    assert (parse_name_to_contact("Henri Henrisson", mock_title_repository) == contact)


def test_parse_single_title(mock_title_repository):
    contact = Contact()
    contact.titel = "Dr."
    contact.nachname = "Henrisson"
    assert (parse_name_to_contact("Dr. Henrisson", mock_title_repository) == contact)


def test_parse_single_title_full_name(mock_title_repository):
    contact = Contact()
    contact.titel = "Dr."
    contact.vorname = "Benjamin"
    contact.nachname = "Henrisson"
    assert (parse_name_to_contact("Dr. Benjamin Henrisson", mock_title_repository) == contact)
