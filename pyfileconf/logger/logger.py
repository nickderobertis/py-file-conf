import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


class CustomFormatter(logging.Formatter):
    debug_formatter = logging.Formatter(
        "%(asctime)s: %(name)s - %(filename)s L%(lineno)s - %(levelname)s - %(message)s"
    )
    other_formatter = logging.Formatter(
        '[%(name)s %(levelname)s]: %(message)s'
    )

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno <= logging.DEBUG:
            return self.debug_formatter.format(record)
        return self.other_formatter.format(record)


logger = logging.getLogger("pyfileconf")
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def add_file_handler():
    from pyfileconf.opts import options

    if options.log_folder is None:
        raise ValueError(f'Cannot enable logging file handler as no log_folder is set in options')
    if not os.path.exists(options.log_folder):
        os.makedirs(options.log_folder)
    log_path = os.path.join(options.log_folder, 'pyfileconf.log')
    fh = TimedRotatingFileHandler(
        log_path, when=options.log_file_rollover_freq, backupCount=options.log_file_num_keep
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(CustomFormatter())
    logger.addHandler(fh)


def remove_file_handler():
    timed_handlers = [h for h in logger.handlers if isinstance(h, TimedRotatingFileHandler)]
    if len(timed_handlers) != 1:
        raise ValueError(f'Could not remove pyfileconf TimedRotatingFileHandler. '
                         f'Expected 1 registered TimedRotatingFileHandler, '
                         f'got {len(timed_handlers)}')
    timed_handler = timed_handlers[0]
    timed_handler.close()
    logger.handlers = [h for h in logger.handlers if h is not timed_handler]
