from domain.contact import Contact
from domain.briefanrede import generate_briefanrede

def test_briefanrede_empty():
    contact = Contact()
    assert (generate_briefanrede(contact) == "Sehr geehrte Damen und Herren")


def test_briefanrede_only_firstname():
    contact = Contact()
    contact.vorname = "Harald"
    assert (generate_briefanrede(contact) == "Sehr geehrte Damen und Herren")


def test_briefanrede_name():
    contact = Contact()
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    assert (generate_briefanrede(contact) == "Sehr geehrte Damen und Herren")


def test_briefanrede_name_gender():
    contact = Contact()
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Sehr geehrter Herr Heimer")


def test_briefanrede_name_gender_title():
    contact = Contact()
    contact.titel = "Dr."
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Sehr geehrter Herr Dr. Heimer")


def test_briefanrede_name_gender_multiple_title():
    contact = Contact()
    contact.titel = "Dipl.-Ing. Dr. Rer. Nat."
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Sehr geehrter Herr Dipl.-Ing. Dr. Rer. Nat. Heimer")


def test_briefanrede_name_gender_language():
    contact = Contact()
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    contact.sprache = "fr"
    assert (generate_briefanrede(contact) == "Monsieur Heimer")

