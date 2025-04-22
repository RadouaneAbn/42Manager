import logging
import os
from config import LOG_FILE

log_header = "level\tmodule\t[dd/MMM/YYYY hh:mm:ss]\tmessage"

class HeaderFileHandler(logging.FileHandler):
    """A class to create a header for the log file"""
    def __init__(self, filename, header, mode='a', encoding=None, delay=False):
        """Initiate the file hundler"""
        write_header = not os.path.exists(filename) or os.stat(filename).st_size == 0
        super().__init__(filename, mode, encoding, delay)
        if write_header:
            self.stream.write(header + '\n')

handler = HeaderFileHandler(LOG_FILE, log_header, encoding='utf-8')

formatter = logging.Formatter(
    '%(levelname)s\t%(module)s\t%(asctime)s\t%(message)s',
    datefmt='[%d/%b/%Y %H:%M:%S]'
)

logger = logging.getLogger("42Manager")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def log_info(message):
    logger.info(f'"{message}"')

def log_warning(message):
    logger.warning(f'"{message}"')

def log_error(message):
    logger.error(f'"{message}"')
