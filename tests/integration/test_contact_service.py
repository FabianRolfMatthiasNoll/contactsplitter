from domain.contact import Contact
from application.contact_service import ContactService



def test_contact_service_process_empty(contact_service):
    result = contact_service.process("")
    expected = Contact(
        inaccuracies = [
            'Vorname fehlt',
            'Nachname fehlt',
        ],
        review_fields = [
            'vorname',
            'nachname'
        ]
    )
    result.briefanrede = '' # this is AI generated, and thus does not make sense to be tested.

    assert (result == expected)
    

def test_contact_service_process_lastname_only(contact_service):
    result = contact_service.process("Schlüter")
    expected = Contact(
        nachname = "Schlüter",
        sprache = "de",
        inaccuracies = [
            'Vorname fehlt',
        ],
        review_fields = [
            'vorname',
        ]
    )
    result.briefanrede = ''

    assert (result == expected)
    

def test_contact_service_process_name_only(contact_service):
    result = contact_service.process("Fabian Schlüter")
    expected = Contact(
        vorname = "Fabian",
        nachname = "Schlüter",
        geschlecht = "m",
        sprache = "de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''
    

    assert (result == expected)


def test_contact_service_process_salutation_untypical(contact_service):
    result = contact_service.process("Frau Fabian Schlüter")
    expected = Contact(
        anrede = "Frau",
        vorname = "Fabian",
        nachname = "Schlüter",
        geschlecht = "w",
        sprache = "de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''


    assert (result == expected)


def test_contact_service_process_inverted_name_order(contact_service):
    result = contact_service.process("Herr Schlüter, Fabian")
    expected = Contact(
        anrede = "Herr",
        vorname = "Fabian",
        nachname = "Schlüter",
        geschlecht = "m",
        sprache = "de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''


    assert (result == expected)


def test_contact_service_process_title(contact_service):
    result = contact_service.process("Frau Dr. Maria von Schäfer-Karrenberger")
    expected = Contact(
        anrede = "Frau",
        titel = "Dr.",
        vorname = "Maria",
        nachname = "Von Schäfer-Karrenberger",
        geschlecht = "w",
        sprache = "de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''


    assert (result == expected)


def test_contact_service_process_double_titles(contact_service):
    result = contact_service.process("Herr Dr. Prof. Max Mustermann")
    expected = Contact(
        anrede="Herr",
        titel="Dr. Prof.",
        vorname="Max",
        nachname="Mustermann",
        geschlecht="m",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_foreign_name_english(contact_service):
    result = contact_service.process("Mr. William Shakespeare")
    expected = Contact(
        anrede="Mr",
        vorname="William",
        nachname="Shakespeare",
        geschlecht="m",
        sprache="en"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_foreign_name_french(contact_service):
    result = contact_service.process("Madame Marie Curie")
    expected = Contact(
        anrede="Madame",
        vorname="Marie",
        nachname="Curie",
        geschlecht="w",
        sprache="fr"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_foreign_name_italian(contact_service):
    result = contact_service.process("Signor Dante Alighieri")
    expected = Contact(
        anrede="Signor",
        vorname="Dante",
        nachname="Alighieri",
        geschlecht="m",
        sprache="it"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_foreign_name_spanish(contact_service):
    result = contact_service.process("Señora Montserrat Caballé")
    expected = Contact(
        anrede="Señora",
        vorname="Montserrat",
        nachname="Caballé",
        geschlecht="w",
        sprache="es"
    )
    
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_with_hyphenated_name(contact_service):
    result = contact_service.process("Herr Karl-Heinz Müller-Schmidt")
    expected = Contact(
        anrede="Herr",
        vorname="Karl-Heinz",
        nachname="Müller-Schmidt",
        geschlecht="m",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_no_anrede(contact_service):
    result = contact_service.process("Max Mustermann")
    expected = Contact(
        vorname="Max",
        nachname="Mustermann",
        geschlecht="m",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_extra_whitespace(contact_service):
    result = contact_service.process("  Frau   Anna   Schmidt   ")
    expected = Contact(
        anrede="Frau",
        vorname="Anna",
        nachname="Schmidt",
        geschlecht="w",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_complex_mixed_order(contact_service):
    result = contact_service.process("Prof. Dr. von Trapp, Maria")
    expected = Contact(
        titel="Prof. Dr.",
        vorname="Maria",
        nachname="Von Trapp",
        geschlecht="w",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_nonstandard_punctuation(contact_service):
    result = contact_service.process("Herr, Dr., Max, Mustermann")
    expected = Contact(
        anrede="Herr",
        titel="Dr.",
        vorname="Max",
        nachname="Mustermann",
        geschlecht="m",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected



def test_contact_service_process_long_name_chain(contact_service):
    result = contact_service.process("Herr Dr. Johann Georg Christoph Friedrich von Schiller")
    expected = Contact(
        anrede="Herr",
        titel="Dr.",
        vorname="Johann Georg Christoph Friedrich",
        nachname="Von Schiller",
        geschlecht="m",
        sprache="de"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_nobility_prefix(contact_service):
    result = contact_service.process("Herr Graf Max von Muster")
    expected = Contact(
        anrede="Herr",
        vorname="Max",
        titel="Gräf.",
        nachname="Von Muster",
        geschlecht="m",
        sprache="de"
    )

    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected


def test_contact_service_process_foreign_special_characters(contact_service):
    result = contact_service.process("Señor José Ángel García")
    expected = Contact(
        anrede="Señor",
        vorname="José Ángel",
        nachname="García",
        geschlecht="m",
        sprache="es"
    )
    # the exact text is AI generated, therefore it does not make sense to compare this.
    assert result.briefanrede != ''
    result.briefanrede = ''

    assert result == expected
