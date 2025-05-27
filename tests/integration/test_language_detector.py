from domain.contact import Contact
from infrastructure.openai_service import OpenAIService

def test_language_detector():
    expectations = {
        # German
        "Johann Sebastian Bach": "de",
        "Clara Schumann": "de",

        # English
        "William Shakespeare": "en",
        "Jane Austen": "en",

        # French
        "Victor Hugo": "fr",
        "Marie Curie": "fr",

        # Italian
        "Dante Alighieri": "it",
        "Sophia Loren": "it",

        # Spanish
        "Miguel de Cervantes": "es",
        "Montserrat Caballé": "es"
    }

    ai = OpenAIService()

    results = { name: ai.detect_language(name) for name in expectations.keys() }
    assert (results == expectations)
