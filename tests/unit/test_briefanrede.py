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


def test_briefanrede_name_male_title():
    contact = Contact()
    contact.titel = "Dr."
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Sehr geehrter Herr Dr. Heimer")


def test_briefanrede_name_female_title():
    contact = Contact()
    contact.titel = "Dr."
    contact.vorname = "Ines"
    contact.nachname = "Heimer"
    contact.geschlecht = "w"
    assert (generate_briefanrede(contact) == "Sehr geehrte Frau Dr. Heimer")


def test_briefanrede_name_gender_multiple_title():
    contact = Contact()
    contact.titel = "Dipl.-Ing. Dr. Rer. Nat."
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Sehr geehrter Herr Dipl.-Ing. Dr. Rer. Nat. Heimer")


def test_briefanrede_name_gender_french_male():
    contact = Contact()
    contact.vorname = "Harald"
    contact.nachname = "Heimer"
    contact.geschlecht = "m"
    contact.sprache = "fr"
    assert (generate_briefanrede(contact) == "Monsieur Heimer")


def test_briefanrede_name_gender_french_female():
    contact = Contact()
    contact.vorname = "Geraldine"
    contact.nachname = "Monceur"
    contact.geschlecht = "w"
    contact.sprache = "fr"
    assert (generate_briefanrede(contact) == "Madame Monceur")


def test_briefanrede_name_gender_french_unspecified_gender():
    contact = Contact()
    contact.vorname = "Geraldine"
    contact.nachname = "Monceur"
    contact.geschlecht = "-"
    contact.sprache = "fr"
    assert (generate_briefanrede(contact) == "Messieursdames")


def test_briefanrede_male_english():
    contact = Contact()
    contact.vorname = "Harald"
    contact.nachname = "Smith"
    contact.sprache = "en"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Dear Mr Smith")


def test_briefanrede_female_english():
    contact = Contact()
    contact.vorname = "Layla"
    contact.nachname = "Smith"
    contact.sprache = "en"
    contact.geschlecht = "w"
    assert (generate_briefanrede(contact) == "Dear Ms Smith")


def test_briefanrede_male_english_with_salutation():
    contact = Contact()
    contact.anrede = "Mr. "
    contact.vorname = "Harald"
    contact.nachname = "Smith"
    contact.sprache = "en"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Dear Mr Smith")


def test_briefanrede_female_english_with_salutation():
    contact = Contact()
    contact.anrede = "Ms. "
    contact.vorname = "Layla"
    contact.titel = "Dr. "
    contact.nachname = "Smith"
    contact.sprache = "en"
    contact.geschlecht = "w"
    assert (generate_briefanrede(contact) == "Dear Dr. Smith")


def test_briefanrede_female_italian():
    contact = Contact()
    contact.vorname = "Ina"
    contact.nachname = "Pocar"
    contact.sprache = "it"
    contact.geschlecht = "w"
    assert (generate_briefanrede(contact) == "Gentile Signora Pocar")


def test_briefanrede_male_italian():
    contact = Contact()
    contact.vorname = "Roberto"
    contact.nachname = "Pocar"
    contact.sprache = "it"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Egregio Signor Pocar")


def test_briefanrede_italian_unspecified_gender():
    contact = Contact()
    contact.vorname = "Roberto"
    contact.nachname = "Pocar"
    contact.sprache = "it"
    assert (generate_briefanrede(contact) == "Egregi Signori")


def test_briefanrede_female_spanish():
    contact = Contact()
    contact.vorname = "Maria"
    contact.nachname = "Juan"
    contact.sprache = "es"
    contact.geschlecht = "w"
    assert (generate_briefanrede(contact) == "Estimada Señora Juan")


def test_briefanrede_male_spanish():
    contact = Contact()
    contact.vorname = "Miguel"
    contact.nachname = "Invenel"
    contact.sprache = "es"
    contact.geschlecht = "m"
    assert (generate_briefanrede(contact) == "Estimado Señor Invenel")


def test_briefanrede_spanish_unspecified_gender():
    contact = Contact()
    contact.vorname = "Miguel"
    contact.nachname = "Invenel"
    contact.sprache = "es"
    assert (generate_briefanrede(contact) == "Estimados Señores y Señoras")

