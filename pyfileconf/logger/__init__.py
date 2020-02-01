from contextlib import contextmanager
import datetime
import sys
import os

@contextmanager
def stdout_also_logged(log_folder: str = None):
    stdout_logger = Logger(log_folder)
    sys.stdout = stdout_logger  # type: ignore
    yield log_folder
    sys.stdout = stdout_logger.terminal
    stdout_logger.log.close()


class Logger(object):
    def __init__(self, log_folder: str = None):
        self.terminal = sys.stdout
        log_path = _log_filename() if log_folder is None else os.path.join(log_folder, _log_filename())
        self.log = open(log_path, "a", encoding='utf8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

def _log_filename():
    creation_time = str(datetime.datetime.now().replace(microsecond=0)).replace(':', '.')
    return f'{creation_time}.log'