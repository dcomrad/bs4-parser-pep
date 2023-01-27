import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_URL, EXPECTED_STATUS, MAIN_DOC_URL,
                       PEP_URL, WHATS_NEW_URL)
from exceptions import (ParserConnectionFailedException,
                        ParserDataConflictException, ParserFindDataException,
                        ParserFindTagException)
from outputs import control_output
from pep import PythonPEP
from utils import find_tag, get_response, get_soup, select_tag

logger = logging.getLogger(__name__)
configure_logging(logger)


def whats_new(session):
    soup = get_soup(session, WHATS_NEW_URL)

    div = select_tag(soup, '#what-s-new-in-python > div.toctree-wrapper')
    items = div.select('li.toctree-l1')

    links = [urljoin(WHATS_NEW_URL, item.a['href']) for item in items]

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    messages_for_logging = []
    for link in tqdm(links):
        try:
            new_soup = get_soup(session, link)

            h1 = select_tag(new_soup, 'div.body section > h1')
            dl = new_soup.select_one('div.body section > dl.field-list')

            result.append(
                (link,
                 h1.text,
                 dl.text.replace('\n', ' ').strip() if dl else '')
            )
        except ParserConnectionFailedException as ex:
            messages_for_logging.append(ex)
        except ParserFindTagException as ex:
            messages_for_logging.append(ex)

    for message in messages_for_logging:
        logger.error(message)

    return result


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)

    ul_tags = soup.select('div.sphinxsidebarwrapper > ul')
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

    table_tag = select_tag(soup, 'div.body > table.docutils')
    a_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(DOWNLOADS_URL, a_tag.get('href'))

    # подготовка папки для записи файла
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    # При попытке переноса этой переменной в constants, не проходят тесты
    # по причине того, что они не видят папку downloads, которая в ходе тестов
    # фактически создаётся в папке src проекта, а тесты ищут её во временной
    # папке $TMP\pytest-of-Aleksandr\pytest-46\test_download0\downloads
    # Почему так происходит я разобраться не смог, но предполагаю, что это
    # как-то связано с оптимизацией при построении байт-кода
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    # скачивание файла
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logger.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_URL)

    lines = soup.select('#numerical-index tbody tr')
    peps = []
    for line in lines:
        abbr, number, name, *_ = line.find_all('td')
        type_key, status_key = abbr.string[0], abbr.string[1:]
        link = find_tag(name, 'a').get('href')
        peps.append(
            PythonPEP(number.string, name.string, type_key, status_key,
                      urljoin(PEP_URL, link))
        )

    result = {'Unknown': 0}
    messages_for_logging = []
    for pep_item in tqdm(peps):
        status = None
        try:
            status = pep_item.get_status(session)
        except ParserConnectionFailedException as ex:
            messages_for_logging.append(ex)
        except ParserDataConflictException as ex:
            messages_for_logging.append(ex)

        if status is None:
            message = f'Ошибка получения статуса для PEP {pep_item.link}'
            messages_for_logging.append(message)
        if status not in EXPECTED_STATUS[pep_item.status_key]:
            result['Unknown'] += 1
        else:
            result[status] = result[status] + 1 if result.get(status) else 1

    for message in messages_for_logging:
        logger.error(message)

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
    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    main()
