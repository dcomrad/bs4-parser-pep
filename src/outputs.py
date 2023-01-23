import csv
import logging
import datetime as dt

from prettytable import PrettyTable
from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    output = cli_args.output

    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    """Печатает результат построчно в консоль."""
    for row in results:
        print(*row)


def pretty_output(results):
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
    results_dir.mkdir(exist_ok=True)

    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    filename = f'{cli_args.mode}_{now_formatted}.csv'
    file_path = results_dir / filename
    with open(file_path, 'w', encoding='UTF-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
