from domain.contact import Contact
from infrastructure.openai_service import OpenAIService

def test_gender_detector():
    expectations = {
        "Ralf"            : "m",
        "Karla"           : "w",
        "Peter"           : "m",
        "Frederike"       : "w",
        "Marius-Martin"   : "m",
        "Maria-Pia-Junis" : "w",
    }

    ai = OpenAIService()

    results = { name: ai.detect_gender(name) for name in expectations.keys() }
    assert (results == expectations)
