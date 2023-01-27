import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from configs import configure_logging
from constants import BASE_DIR, DATETIME_FORMAT, DEFAULT, FILE, PRETTY

logger = logging.getLogger(__name__)
configure_logging(logger)


def control_output(results, cli_args):
    output = cli_args.output or DEFAULT
    OUTPUT_MODE[output](results, cli_args)


def pretty_output(results, *args):
    """Печатает результат в виде красивой консольной таблицы."""
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Печатает результат в файл в формате csv."""
    results_dir = BASE_DIR / 'results'
    # При попытке переноса этой переменной в constants, не проходят тесты
    # по причине того, что они не видят папку results, которая в ходе тестов
    # фактически создаётся в папке src проекта, а тесты ищут её во временной
    # папке $TMP\...\pytest-46\test_control_output_file_Names0\results\
    # Почему так происходит я разобраться не смог, но предполагаю, что это
    # как-то связано с оптимизацией при построении байт-кода
    results_dir.mkdir(exist_ok=True)
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    filename = f'{cli_args.mode}_{now_formatted}.csv'
    file_path = results_dir / filename
    with open(file_path, 'w', encoding='UTF-8') as file:
        writer = csv.writer(file, dialect=csv.unix_dialect)
        writer.writerows(results)

    logger.info(f'Файл с результатами был сохранён: {file_path}')


def default_output(results, *args):
    """Печатает результат построчно в консоль."""
    for row in results:
        print(*row)


OUTPUT_MODE = {
    PRETTY: pretty_output,
    FILE: file_output,
    DEFAULT: default_output,
}
