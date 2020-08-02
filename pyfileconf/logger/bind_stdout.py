import sys
from contextlib import contextmanager

from pyfileconf.logger.logger import logger


@contextmanager
def stdout_also_logged():
    stdout_logger = StdoutLogger()
    sys.stdout = stdout_logger  # type: ignore
    yield stdout_logger
    sys.stdout = stdout_logger.terminal


class StdoutLogger(object):
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        if message != '\n':
            logger.info(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass
