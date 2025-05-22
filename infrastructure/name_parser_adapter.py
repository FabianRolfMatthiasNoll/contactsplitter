from application.interfaces import INameParser, ITitleRepository
from domain.contact import Contact
from domain.name_parser import parse_name_to_contact


class DomainNameParser(INameParser):
    def __init__(self, title_repo: ITitleRepository):
        self.title_repo = title_repo

    def parse(self, raw_input: str) -> Contact:
        return parse_name_to_contact(raw_input, self.title_repo)
