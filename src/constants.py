from pathlib import Path
from urllib.parse import urljoin

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
RESULTS_DIR = BASE_DIR / 'results'
DOWNLOADS_DIR = BASE_DIR / 'downloads'

LOG_FILE = LOG_DIR / 'parser.log'

MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
DOWNLOADS_URL = urljoin(MAIN_DOC_URL, 'download.html')
PEP_URL = 'https://peps.python.org/'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_TYPE = ('I', 'P', 'S')
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

LOGGER_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
LOGGER_DT_FORMAT = '%d.%m.%Y %H:%M:%S'

PRETTY = 'pretty'
FILE = 'file'
DEFAULT = ''
