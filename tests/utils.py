import os
import shutil
from typing import Callable, Type, Optional, List, Dict, Union


def delete_project(path: str, logs_path: str,
                   specific_class_config_dicts: Optional[List[Dict[str, Union[str, Type, List[str]]]]] = None,):
    all_paths = [
        os.path.join(path, 'defaults'),
        os.path.join(path, 'custom_defaults'),
        os.path.join(path, 'pipeline_dict.py'),
        logs_path,
    ]
    for specific_class_config in specific_class_config_dicts:
        name = specific_class_config['name']
        all_paths.append(os.path.join(path, f'{name}_dict.py'))
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


def nested_pipeline_dict_str_with_obj(func: Callable, section_key: str, func_key: str, func_module: str) -> str:
    return f'from {func_module} import {func.__name__}\n\npipeline_dict = {{\n\t"{section_key}": {{\n\t\t"{func_key}": [{func.__name__}],\n\t}},\n}}\n'


def class_dict_str(name: str, key: str, value: str) -> str:
    return f'\n{name} = {{\n\t"{key}": ["{value}"],\n}}\n'


def nested_class_dict_str(name: str, section_key: str, key: str, value: str) -> str:
    return f'\n{name} = {{\n\t"{section_key}": {{\n\t\t"{key}": ["{value}"],\n\t}},\n}}\n'
