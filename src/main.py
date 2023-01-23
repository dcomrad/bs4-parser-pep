import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    section = find_tag(soup, 'section', {'id': 'what-s-new-in-python'})
    section = find_tag(section, 'div', {'class': 'toctree-wrapper'})

    items = section.ul.find_all(name='li', class_='toctree-l1')
    links = [urljoin(whats_new_url, item.a['href']) for item in items]

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for link in tqdm(links):
        response = get_response(session, link)
        if response is None:
            return

        soup = BeautifulSoup(response.text, features='lxml')

        main_div = find_tag(soup, 'div', {'class': 'body', 'role': 'main'})
        section = find_tag(main_div, 'section')

        h1 = find_tag(section, 'h1', recursive=False)
        dl = section.find(name='dl', recursive=False)

        result.append(
            (link, h1.text, dl.text.replace('\n', ' ').strip() if dl else '')
        )

    return result


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    for link in a_tags:
        text_matched = re.search(pattern, link.text)
        if text_matched:
            result.append(
                (link['href'], *text_matched.group('version', 'status'))
            )

    return result


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    main_tag = find_tag(soup, 'div', {'class': 'body', 'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})

    # поиск ссылки на искомый файл
    a_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(downloads_url, a_tag.get('href'))

    # подготовка папки для записи файла
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    # скачивание файла
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
