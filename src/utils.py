from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserConnectionFailedException, ParserFindTagException

connection_error = 'Возникла ошибка при загрузке страницы ({link})'
find_tag_error = 'Не найден тег {tag} {attrs}'
select_tag_error = 'Не найден тег {selector}'


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ParserConnectionFailedException(
            connection_error.format(link=url)
        )


def get_soup(session, url):
    response = get_response(session, url)
    return BeautifulSoup(response.text, features='lxml')


def find_tag(soup, tag, attrs=None, recursive=True):
    searched_tag = soup.find(tag,
                             attrs=({} if attrs is None else attrs),
                             recursive=recursive)
    if searched_tag is None:
        raise ParserFindTagException(
            find_tag_error.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def select_tag(soup, selector):
    searched_tag = soup.select_one(selector)
    if searched_tag is None:
        raise ParserFindTagException(
            select_tag_error.format(selector=selector)
        )
    return searched_tag
