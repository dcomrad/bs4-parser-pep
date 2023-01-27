class ParserConnectionFailedException(Exception):
    """Вызывается, когда парсер не может получить данные по URL."""


class ParserFindDataException(Exception):
    """Вызывается, когда парсер не может найти необходимые данные по URL."""


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
