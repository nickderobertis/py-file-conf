import importlib.util
from types import ModuleType
import sys

def get_user_defined_dict_from_filepath(filepath: str, module_name: str=None) -> dict:
    module = _load_file_as_module(filepath, name=module_name)
    return _get_user_defined_dict_from_module(module)

def _get_user_defined_dict_from_module(module: ModuleType) -> dict:
    out_dict = {}
    for key, value in module.__dict__.items():
        if key.startswith('__') or isinstance(value, ModuleType):
            continue
        out_dict.update({key: value})

    return out_dict


def _load_file_as_module(filepath: str, name: str= 'module.name') -> ModuleType:
    if name is None:
        name = 'module.name'
        add_to_sys = False
    else:
        add_to_sys = True

    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if add_to_sys:
        sys.modules.update({name: module})

    return module