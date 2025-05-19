# infrastructure/openai_service.py

import os
import time
import logging
from typing import Optional

from openai import OpenAI

from domain.contact import Contact

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service für:
      - Geschlechtserkennung
      - Spracherkennung
      - Briefanrede-Generierung via GPT-4o

    Mit:
      * Exponential Backoff bei API-Fehlern
      * Fallback auf Generic-Salutation, falls alle Versuche fehlschlagen
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenAI API key required (env OPENAI_API_KEY or param).")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _request_chat_completion(self, system: str, user: str) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                )
                # .choices list und .message.content sind in jedem Release vorhanden
                return resp.choices[0].message.content.strip()
            except Exception as e:
                wait = self.backoff_factor * (2 ** (attempt - 1))
                logger.warning(
                    f"OpenAI API attempt {attempt} failed ({e}), retry in {wait}s"
                )
                time.sleep(wait)
        logger.error("All OpenAI attempts failed, returning empty string.")
        return ""

    def detect_gender(self, first_name: str) -> str:
        if not first_name:
            return "-"
        system = (
            "You are an assistant that classifies a first name as male, "
            "female, or unknown. Answer with 'm', 'w', or '-' exactly."
        )
        user = f"First name: {first_name}"
        raw = self._request_chat_completion(system, user).lower()
        if raw in {"m", "male", "man"}:
            return "m"
        if raw in {"w", "female", "woman"}:
            return "w"
        return "-"

    def detect_language(self, name: str) -> str:
        if not name:
            return ""
        system = (
            "You are an assistant that detects the language/origin of a name. "
            "Answer with one of: de, en, fr, it, es, or '-' if unknown."
        )
        user = f"Name: {name}"
        raw = self._request_chat_completion(system, user).lower()
        mapping = {
            "deutsch": "de",
            "german": "de",
            "de": "de",
            "englisch": "en",
            "english": "en",
            "en": "en",
            "franz": "fr",
            "french": "fr",
            "fr": "fr",
            "italien": "it",
            "italian": "it",
            "it": "it",
            "spanisch": "es",
            "spanish": "es",
            "es": "es",
            "-": "",
            "unknown": "",
            "unbekannt": "",
        }
        for key, code in mapping.items():
            if key in raw:
                return code
        return ""

    def generate_briefanrede(self, contact: Contact) -> str:
        """
        Erstelle eine formelle Briefanrede via GPT-4o:
        Verwende alle Felder: anrede, titel, vorname, nachname, sprache.
        """
        # Kontext-Zusammenbau
        parts = []
        for label, val in [
            ("Anrede", contact.anrede),
            ("Titel", contact.titel),
            ("Vorname", contact.vorname),
            ("Nachname", contact.nachname),
            ("Sprache", contact.sprache),
        ]:
            if val:
                parts.append(f"{label}: {val}")
        context = "\n".join(parts)

        system = (
            "You are a formal correspondence assistant. "
            "Given the following contact details, generate a polite letter salutation "
            "in the appropriate language and style."
        )
        user = f"{context}\n\nGenerate the salutation:"
        result = self._request_chat_completion(system, user)
        return result or "Sehr geehrte Damen und Herren"
