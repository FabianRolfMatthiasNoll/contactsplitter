import json
import os
from typing import Dict
from domain.constants import DEFAULT_TITLES


class TitleRepository:
    """
    Lädt und verwaltet die Titelliste aus einer JSON-Datei.
    Wenn die Datei fehlt oder unvollständig ist, wird sie mit DEFAULT_TITLES
    initialisiert bzw. synchronisiert.
    """

    def __init__(self, file_path: str):
        """
        :param file_path: Pfad zur titles.json
        """
        self.file_path = file_path
        self.titles: Dict[str, str] = {}

    def load(self) -> None:
        """
        Lädt die JSON-Datei. Falls sie nicht existiert, wird sie mit
        DEFAULT_TITLES erzeugt. Wenn Einträge in DEFAULT_TITLES fehlen,
        werden sie ergänzt und die Datei aktualisiert.
        """
        # 1) Existiert die Datei?
        if not os.path.exists(self.file_path):
            # Anlage mit allen DEFAULT_TITLES
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_TITLES, f, ensure_ascii=False, indent=2)
            self.titles = DEFAULT_TITLES.copy()
            return

        # 2) Datei einlesen
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("titles.json must contain an object")
            except Exception:
                # Defekt: überschreiben
                data = {}
        # 3) Prüfen, ob DEFAULT_TITLES ergänzt werden müssen
        updated = False
        for key, val in DEFAULT_TITLES.items():
            if key not in data:
                data[key] = val
                updated = True
        if updated:
            # Datei zurückschreiben
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        self.titles = data

    def get_titles(self) -> list[str]:
        """
        Gibt alle Title-Keys und ihre Kurzformen (ohne Punkt) zurück,
        die im Parser als bekannte Titel erkannt werden.
        """
        result: set[str] = set()
        for key, short in self.titles.items():
            # Token für lange Form
            result.add(key)
            # Token für Kurzform (ohne trailing Punkt)
            short_clean = short.rstrip(".").lower()
            result.add(short_clean)
        return list(result)

    def lookup(self, token: str) -> str | None:
        """
        Sucht für einen Title-Token die Kurzform.
        Rückgabe ist z.B. "Dr." oder "Prof." oder None, falls unbekannt.
        """
        return self.titles.get(token.lower())

    def add(self, token: str, shortform: str) -> bool:
        """
        Fügt dynamisch einen neuen Titel hinzu (und speichert ihn
        direkt in titles.json). Gibt True zurück, wenn es ein neuer
        Eintrag war, False, wenn bereits vorhanden.
        """
        key = token.lower()
        if key in self.titles:
            return False
        self.titles[key] = shortform
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.titles, f, ensure_ascii=False, indent=2)
        return True
