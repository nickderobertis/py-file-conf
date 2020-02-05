from typing import List, Any, Tuple, Iterator
from types import ModuleType
import sys

from pyfileconf.exceptions.imports import CouldNotDetermineModuleForObjectException
from pyfileconf.imports.logic.load.skipmodules import skip_modules
from pyfileconf.sectionpath.sectionpath import SectionPath


def get_imported_obj_variable_name(obj, module: ModuleType) -> str:
    key_list, value_list = _get_module_keys_and_values_lists(module)
    return _get_key_matching_value(obj, key_list, value_list)


def get_module_and_name_imported_from(obj, search_list: List[str]=None) -> Tuple[ModuleType, str]:
    if search_list is None:
        search_list = list(sys.modules.keys())

    for module_name in search_list:

        # skip modules which were causing issues
        if _should_skip_module(module_name):
            continue

        module = sys.modules[module_name]
        if _obj_in_module(obj, module):
            return module, module_name

    raise CouldNotDetermineModuleForObjectException(f'could not find {obj} in {search_list}')

def is_imported_name(name: str, search_list: List[str]=None) -> bool:
    if search_list is None:
        search_list = list(sys.modules.keys())

    for module_name in search_list:

        # skip modules which were causing issues
        if _should_skip_module(module_name):
            continue

        module = sys.modules[module_name]
        if _name_in_module(name, module):
            return True

    return False

def is_imported_obj(obj, search_list: List[str]=None) -> bool:
    if search_list is None:
        search_list = list(sys.modules.keys())

    for module_name in search_list:

        # skip modules which were causing issues
        if _should_skip_module(module_name):
            continue

        module = sys.modules[module_name]
        if _obj_in_module(obj, module):
            return True

    return False

def _is_imported_from(name: str, search_list: List[str]=None) -> List[str]:
    if search_list is None:
        search_list = list(sys.modules.keys())

    matched_modules = []
    for module_name in search_list:

        # skip modules which were causing issues
        if _should_skip_module(module_name):
            continue

        module = sys.modules[module_name]
        if _name_in_module(name, module):
            matched_modules.append(module_name)

    return matched_modules

def _get_key_matching_value(value, key_list, value_list) -> str:
    for i, match_value in enumerate(value_list):
        if value is match_value:
            return key_list[i]
    raise ValueError(f'could not find {value} in {value_list}')


def _get_module_keys_and_values_lists(module: ModuleType) -> Tuple[List[str],List[Any]]:
    key_list = []
    value_list = []
    for key, value in _module_key_value_generator(module):
        key_list.append(key)
        value_list.append(value)

    return key_list, value_list


def _module_key_value_generator(module: ModuleType) -> Iterator[Tuple[str, Any]]:
    for key in dir(module):
        yield key, getattr(module, key)


def _obj_in_module(obj, module: ModuleType) -> bool:
    for key in dir(module):
        if obj is getattr(module, key):
            return True

    return False

def _name_in_module(name: str, module: ModuleType) -> bool:
    return name in dir(module)


def _should_skip_module(name: str) -> bool:
    """
    Check if module section path ends with a section path in skip_models
    """
    module_section_path = SectionPath(name)
    for skip_name in skip_modules:
        skip_sp = SectionPath(skip_name)
        if module_section_path.endswith(skip_sp):
            return True
    return False
