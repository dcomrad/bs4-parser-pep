import logging

from requests import RequestException

from configs import configure_logging
from exceptions import ParserFindTagException

logger = logging.getLogger(__name__)
configure_logging(logger)


def get_connection_err_msg(link: str):
    return f'Возникла ошибка при загрузке страницы ({link})'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logger.exception(get_connection_err_msg(url), stack_info=True)


def find_tag(soup, tag, attrs=None, recursive=True):
    searched_tag = soup.find(tag, attrs=(attrs or {}), recursive=recursive)
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logger.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
