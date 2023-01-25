import argparse
import logging
from logging.handlers import RotatingFileHandler
from sys import stdout

from constants import BASE_DIR

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')

    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )

    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )

    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )

    return parser


def configure_logging(logger):
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'

    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler(stdout)
    f_handler = RotatingFileHandler(log_file,
                                    maxBytes=10**6,
                                    backupCount=5,
                                    encoding='UTF-8')

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DT_FORMAT)
    c_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
