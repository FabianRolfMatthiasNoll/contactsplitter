"""Repository for managing known title strings, stored in a JSON file."""
import json
import logging
import os

logger = logging.getLogger(__name__)

class TitleRepository:
    def __init__(self, filepath: str = "titles.json"):
        """
        Initialize the TitleRepository with path to JSON file.
        """
        self.filepath = filepath
        self.known_titles = []  # list of known title strings
        self._title_set = set()  # for quick membership checks (normalized to lower, no trailing dot)

    def load(self) -> None:
        """Load titles from the JSON file into memory."""
        if not os.path.isfile(self.filepath):
            # If file doesn't exist, initialize an empty list file
            self.known_titles = []
            self._title_set = set()
            try:
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.known_titles, f, ensure_ascii=False, indent=2)
                logger.info(f"Created new titles.json at {self.filepath}.")
            except Exception as e:
                logger.error(f"Failed to create title file {self.filepath}: {e}")
            return
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                # Normalize titles by removing trailing dots and whitespace
                cleaned = []
                for t in data:
                    if isinstance(t, str):
                        title_clean = t.strip()
                        # Remove trailing dot for consistency
                        if title_clean.endswith('.'):
                            title_clean = title_clean[:-1]
                        if title_clean:
                            cleaned.append(title_clean)
                # Remove duplicates (case-insensitive) while preserving order
                seen = set()
                unique_cleaned = []
                for t in cleaned:
                    tlower = t.lower()
                    if tlower not in seen:
                        seen.add(tlower)
                        unique_cleaned.append(t)
                self.known_titles = unique_cleaned
                # Prepare set for membership (normalized to lowercase, no dot)
                self._title_set = {t.lower() for t in unique_cleaned}
            else:
                logger.warning(f"Unexpected format in title file {self.filepath}, resetting to empty list.")
                self.known_titles = []
                self._title_set = set()
        except Exception as e:
            logger.error(f"Error loading titles from {self.filepath}: {e}")
            self.known_titles = []
            self._title_set = set()

    def add(self, title: str) -> bool:
        """
        Add a new title to the repository (in memory and to the file).
        Returns True if added, False if already present or invalid.
        """
        if not title or not isinstance(title, str):
            return False
        title_clean = title.strip()
        if title_clean.endswith('.'):
            title_clean = title_clean[:-1]
        if title_clean == "":
            return False
        key = title_clean.lower()
        if key in self._title_set:
            logger.info(f"Title '{title_clean}' already known, not adding.")
            return False
        # Add new title
        self.known_titles.append(title_clean)
        self._title_set.add(key)
        # Immediately save to file
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.known_titles, f, ensure_ascii=False, indent=2)
            logger.info(f"Added new title '{title_clean}' to {self.filepath}.")
        except Exception as e:
            logger.error(f"Failed to save new title '{title_clean}' to file: {e}")
            return False
        return True

    def get_titles(self) -> list[str]:
        """Get the list of known titles."""
        return list(self.known_titles)
