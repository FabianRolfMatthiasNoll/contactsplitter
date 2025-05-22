from typing import List
from application.interfaces import IHistoryRepository
from domain.contact import Contact


class InMemoryHistoryRepository(IHistoryRepository):
    def __init__(self):
        self._store: List[Contact] = []

    def save(self, contact: Contact) -> None:
        self._store.append(contact)

    def list(self) -> List[Contact]:
        return list(self._store)
