import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR  # тесты требуют наличие этой константы
# from pathlib import Path
# BASE_DIR = Path(__file__).parent
from constants import (DOWNLOADS_DIR, DOWNLOADS_URL, EXPECTED_STATUS,
                       MAIN_DOC_URL, PEP_URL, WHATS_NEW_URL)
from exceptions import ParserConnectionFailedException, ParserFindDataException
from outputs import control_output
from pep import PythonPEP
from utils import find_tag, get_response, get_soup

logger = logging.getLogger(__name__)
configure_logging(logger)


def whats_new(session):
    soup = get_soup(session, WHATS_NEW_URL)

    main_section = find_tag(soup, 'section', {'id': 'what-s-new-in-python'})
    div = find_tag(main_section, 'div', {'class': 'toctree-wrapper'})
    items = div.ul.find_all(name='li', class_='toctree-l1')
    links = [urljoin(WHATS_NEW_URL, item.a['href']) for item in items]

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for link in tqdm(links):
        new_soup = get_soup(session, link)

        main_div = find_tag(new_soup, 'div', {'class': 'body', 'role': 'main'})
        section = find_tag(main_div, 'section')

        h1 = find_tag(section, 'h1', recursive=False)
        dl = section.find(name='dl', recursive=False)

        result.append(
            (link, h1.text, dl.text.replace('\n', ' ').strip() if dl else '')
        )

    return result


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindDataException('Не найден список c версиями Python')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_matched = re.search(pattern, a_tag.text)
        if text_matched:
            version, status = text_matched.groups()
        else:
            version, status = a_tag.text, ''
        result.append((link, version, status))

    return result


def download(session):
    soup = get_soup(session, DOWNLOADS_URL)

    main_tag = find_tag(soup, 'div', {'class': 'body', 'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})

    # поиск ссылки на искомый файл
    a_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(DOWNLOADS_URL, a_tag.get('href'))

    # подготовка папки для записи файла
    filename = archive_url.split('/')[-1]

    DOWNLOADS_DIR.mkdir(exist_ok=True)
    archive_path = DOWNLOADS_DIR / filename

    # скачивание файла
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logger.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_URL)

    used_pep = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_table = find_tag(used_pep, 'tbody')
    lines = pep_table.find_all(name='tr')

    peps = []
    for line in lines:
        abbr, number, name, *_ = line.find_all(name='td')
        type_key, status_key = abbr.string[0], abbr.string[1:]
        link = find_tag(name, 'a').get('href')
        peps.append(
            PythonPEP(number.string, name.string, type_key, status_key,
                      urljoin(PEP_URL, link))
        )

    result = {'Unknown': 0}
    for pep_item in tqdm(peps):
        status = pep_item.get_status(session)
        if status is None:
            msg = f'Ошибка получения статуса для PEP {pep_item}'
            logger.error(msg)

        if status not in EXPECTED_STATUS[pep_item.status_key]:
            result['Unknown'] += 1
        else:
            result[status] = result[status] + 1 if result.get(status) else 1

    result['Total'] = len(peps)

    return [('Статус', 'Количество')] + [(k, v) for k, v in result.items()]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    logger.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logger.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
        logger.info('Парсер завершил работу.')
    except ParserConnectionFailedException as ex:
        logger.error(f'Ошибка соединения: {ex}')
    except ParserFindDataException as ex:
        logger.error(f'Ошибка при попытке парсинга: {ex}')
    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    main()
