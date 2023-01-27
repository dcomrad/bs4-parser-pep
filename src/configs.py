import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (FILE, LOG_DIR, LOG_FILE, LOGGER_DT_FORMAT,
                       LOGGER_FORMAT, PRETTY)


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')

    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера',
    )

    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )

    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY, FILE),
        help='Дополнительные способы вывода данных',
    )

    return parser


def configure_logging(logger):
    LOG_DIR.mkdir(exist_ok=True)

    logger.setLevel(logging.DEBUG)

    f_handler = RotatingFileHandler(LOG_FILE,
                                    maxBytes=10**6,
                                    backupCount=5,
                                    encoding='UTF-8')

    formatter = logging.Formatter(fmt=LOGGER_FORMAT, datefmt=LOGGER_DT_FORMAT)
    f_handler.setFormatter(formatter)

    logger.addHandler(f_handler)
