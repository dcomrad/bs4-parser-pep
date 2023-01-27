import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from configs import configure_logging
from constants import BASE_DIR  # тесты требуют наличие этой константы
from constants import DATETIME_FORMAT, DEFAULT, FILE, PRETTY, RESULTS_DIR

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
    RESULTS_DIR.mkdir(exist_ok=True)
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    filename = f'{cli_args.mode}_{now_formatted}.csv'
    file_path = RESULTS_DIR / filename
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
