from typing import List, Any, Tuple
from types import ModuleType
import sys

def get_imported_obj_variable_name(obj, module: ModuleType) -> str:
    key_list, value_list = _get_module_keys_and_values_lists(module)
    return _get_key_matching_value(obj, key_list, value_list)


def get_module_and_name_imported_from(obj, search_list: List[str]=None) -> Tuple[ModuleType, str]:
    if search_list is None:
        search_list = list(sys.modules.keys())

    for module_name in search_list:
        module = sys.modules[module_name]
        if _obj_in_module(obj, module):
            return module, module_name


def _get_key_matching_value(value, key_list, value_list) -> str:
    for i, match_value in enumerate(value_list):
        if value == match_value:
            return key_list[i]


def _get_module_keys_and_values_lists(module: ModuleType) -> Tuple[List[str],List[Any]]:
    key_list = []
    value_list = []
    for key, value in _module_key_value_generator(module):
        key_list.append(key)
        value_list.append(value)

    return key_list, value_list


def _module_key_value_generator(module: ModuleType) -> Tuple[str, Any]:
    for key in dir(module):
        yield key, getattr(module, key)


def _obj_in_module(obj, module: ModuleType) -> bool:
    for key in dir(module):
        if obj == getattr(module, key):
            return True

    return False
