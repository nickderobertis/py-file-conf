import os
import shutil
from typing import Callable


def delete_project(path: str):
    all_paths = [
        os.path.join(path, 'defaults'),
        os.path.join(path, 'pipeline_dict.py'),
        os.path.join(path, 'data_dict.py'),
        os.path.join(path, 'Logs'),
    ]
    for path in all_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            # Must not exist, maybe add handling for this later
            pass


def pipeline_dict_str_with_obj(func: Callable, func_key: str, func_module: str) -> str:
    return f'from {func_module} import {func.__name__}\n\npipeline_dict = {{\n\t"{func_key}": [{func.__name__}],\n}}\n'
