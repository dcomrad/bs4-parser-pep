import logging

import requests_cache
from bs4 import BeautifulSoup

from constants import EXPECTED_STATUS, EXPECTED_TYPE
from utils import find_tag, get_connection_err_msg, get_response


class PythonPEP:
    """Класс, отображающий сведения о Python Enhancement Proposals"""
    def __init__(self,
                 number: int,
                 name: str,
                 type_key: str,
                 status_key: str,
                 link: str):

        error_msg = ''
        if type_key not in EXPECTED_TYPE:
            error_msg = f'Некорректный ключ типа: {type_key}'
        if status_key not in EXPECTED_STATUS:
            error_msg = f'Некорректный ключ статуса: {status_key}'

        if error_msg:
            logging.error(error_msg)
            raise ValueError(error_msg)

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
        response = get_response(session, self.link)
        if response is None:
            logging.error(get_connection_err_msg(self.link))
            return None

        soup = BeautifulSoup(response.text, features='lxml')
        info_table = find_tag(soup, 'dl', {'class': 'field-list'})

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
            msg = (f'Несовпадающий статус ({self.link})\n'
                   f'Статус в карточке: {self.status}\n'
                   f'Ожидаемые статусы: {EXPECTED_STATUS[self.status_key]}')
            logging.error(msg)

        return self.status
