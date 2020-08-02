from typing import Optional

from pyfileconf.logger.logger import add_file_handler, remove_file_handler


def add_file_handler_if_log_folder_exists_else_remove_handler(attr_name: str, log_folder: Optional[str]):
    if log_folder is not None:
        add_file_handler()
    else:
        remove_file_handler()
