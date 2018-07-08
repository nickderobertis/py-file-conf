from typing import Dict, Union

from dero.manager.imports.logic.load.file import get_user_defined_dict_from_filepath

DictOrStr = Union[Dict, str]

def data_dict_from_file(filepath: str, module_name: str=None) -> Dict[str, DictOrStr]:
    user_defined_dict = get_user_defined_dict_from_filepath(filepath, module_name=module_name)

    if 'data_dict' not in user_defined_dict:
        raise ValueError(f'data dict file {filepath} must contain variable data_dict')

    return user_defined_dict['data_dict']