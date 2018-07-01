import importlib.util
from types import ModuleType
import sys

from dero.manager.imports.logic.load.name import is_imported_name
from dero.manager.imports.models.tracker import ImportTracker

def get_user_defined_dict_from_filepath(filepath: str, module_name: str=None, remove_imports=False,
                                        import_tracker: ImportTracker=None) -> dict:
    module = _load_file_as_module(filepath, name=module_name)
    user_defined_dict = _get_user_defined_dict_from_module(module)
    if remove_imports:
        if import_tracker is None:
            raise ValueError('must pass ImportTracker when passing remove_imports=True')
        return {
            key: value for key, value in user_defined_dict.items() \
            if not is_imported_name(key, import_tracker.imported_modules)
        }
    else:
        return user_defined_dict

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