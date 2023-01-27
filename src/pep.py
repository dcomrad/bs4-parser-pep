import requests_cache

from constants import EXPECTED_STATUS, EXPECTED_TYPE
from exceptions import ParserDataConflictException
from utils import get_soup, select_tag


class PythonPEP:
    """Класс, отображающий сведения о Python Enhancement Proposals"""
    def __init__(self,
                 number: int,
                 name: str,
                 type_key: str,
                 status_key: str,
                 link: str):

        error_message = ''
        if type_key not in EXPECTED_TYPE:
            error_message = f'Некорректный ключ типа: {type_key}'
        if status_key not in EXPECTED_STATUS:
            error_message = f'Некорректный ключ статуса: {status_key}'

        if error_message:
            raise ValueError(error_message)

        self.number = number
        self.name = name
        self.type_key = type_key
        self.status_key = status_key
        self.link = link
        self.status = ''

    def get_status(self, session=None):
        """Возвращает статус PEP. При его отсутствии, получает его со страницы
         самого PEP"""
        if not session:
            session = requests_cache.CachedSession()

        soup = get_soup(session, self.link)
        info_table = select_tag(soup, 'dl.field-list')

        for child in info_table.find_all('dt'):
            if 'Status' in child.strings:
                status_tag = child.next_sibling.next_sibling
                break
        else:
            status_tag = None

        if not status_tag:
            return None

        self.status = status_tag.text

        if self.status not in EXPECTED_STATUS[self.status_key]:
            message = (
                f'Несовпадающий статус ({self.link}); '
                f'Статус в карточке: {self.status}; '
                f'Ожидаемые статусы: {EXPECTED_STATUS[self.status_key]}'
            )
            raise ParserDataConflictException(message)

        return self.status
