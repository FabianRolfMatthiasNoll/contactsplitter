import json
import os
from typing import Dict
from application.interfaces import ITitleRepository
from domain.constants import DEFAULT_TITLES


class TitleRepository(ITitleRepository):
    """
    Lädt und verwaltet die Titelliste aus einer JSON-Datei (titles.json).
    Wenn die Datei fehlt oder ungültig ist, wird sie mit DEFAULT_TITLES neu angelegt.
    Änderungen (add/delete/reset) wirken direkt auf diese Datei.
    """

    def __init__(self, file_path: str):
        """
        :param file_path: Pfad zur titles.json
        """
        self.file_path = file_path
        self.titles: Dict[str, str] = {}

    def load(self) -> None:
        """
        Lädt die titles.json.
        - Existiert sie nicht oder ist defekt → wird neu mit DEFAULT_TITLES angelegt.
        - Sonst wird der Inhalt in self.titles geladen.
        """
        data: Dict[str, str]
        if not os.path.exists(self.file_path):
            data = DEFAULT_TITLES.copy()
            self._save(data)
        else:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if not isinstance(loaded, dict):
                        raise ValueError("Ungültiges Format")
                    data = loaded
            except Exception:
                data = DEFAULT_TITLES.copy()
                self._save(data)
        # Schlüssel normieren auf Kleinbuchstaben
        self.titles = {k.lower(): v for k, v in data.items()}

    def get_titles(self) -> list[str]:
        """
        Gibt alle Langform-Tokens (klein, ohne Punkt) zurück.
        """
        return list(self.titles.keys())

    def lookup(self, token: str) -> str | None:
        """
        Liefert die Kurzform zu einem Token oder None.
        """
        return self.titles.get(token.lower())

    def add(self, langform: str, kurzform: str) -> bool:
        """
        Fügt oder aktualisiert einen Eintrag in titles.json.
        Rückgabe True, wenn sich etwas geändert hat.
        """
        key = langform.strip().lower()
        val = kurzform.strip()
        if self.titles.get(key) == val:
            return False
        self.titles[key] = val
        self._save(self.titles)
        return True

    def delete(self, langform: str) -> bool:
        """
        Entfernt einen Eintrag. Rückgabe True, wenn er vorher existierte.
        """
        key = langform.strip().lower()
        if key in self.titles:
            del self.titles[key]
            self._save(self.titles)
            return True
        return False

    def reset_to_defaults(self) -> None:
        """
        Überschreibt titles.json komplett mit DEFAULT_TITLES.
        """
        data = {k.lower(): v for k, v in DEFAULT_TITLES.items()}
        self.titles = data.copy()
        self._save(data)

    def _save(self, data: Dict[str, str]) -> None:
        """
        Persistiert die gegebene Map in titles.json.
        """
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
