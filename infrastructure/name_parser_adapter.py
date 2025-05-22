from application.interfaces import INameParser
from domain.contact import Contact
from domain.name_parser import parse_name_to_contact


class DomainNameParser(INameParser):
    def __init__(self, title_repo):
        self.title_repo = title_repo

    def parse(self, raw_input: str) -> Contact:
        known_titles = self.title_repo.get_titles()
        return parse_name_to_contact(raw_input, known_titles)
