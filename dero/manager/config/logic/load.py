import importlib.util
from types import ModuleType


def get_user_defined_dict_from_module(module: ModuleType):
    out_dict = {}
    for key, value in module.__dict__.items():
        if key.startswith('__') or isinstance(value, ModuleType):
            continue
        out_dict.update({key: value})

    return out_dict


def load_file_as_module(filepath: str, name: str='module.name'):
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module