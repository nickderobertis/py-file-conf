import warnings
import builtins
from typing import List

from dero.manager.imports.logic.load.name import (
    get_imported_obj_variable_name,
    get_module_and_name_imported_from,
    is_imported_name
)

def dict_as_local_definitions_str(d: dict, module_strs: List[str]=None) -> str:
    lines = []
    for key, value in d.items():
        if is_imported_name(key, module_strs):
            continue # don't need to create assignment strs for imported names
        lines.append(
            _key_value_pair_to_assignment_str(key, value, module_strs=module_strs)
        )

    return '\n' + '\n'.join(lines) +'\n'

def modules_and_items_as_imports_str(module_strs: List[str], config_dict: dict) -> str:

    lines = []
    for arg_name, value in config_dict.items():
        # Don't need to import builtins
        if _is_builtin(value):
            continue

        module, module_name = get_module_and_name_imported_from(value, module_strs)
        variable_name = get_imported_obj_variable_name(value, module)
        line = _module_str_and_variable_to_import_statement(module_name, variable_name)
        if line not in lines:
            # TODO: better handling for imports
            # Was having a problem where imported items are represented twice in the user_defined_dict.
            # Once for assignment to the function, and once for assignment to the name from the import statement
            # Was having trouble removing one from the dictionary
            # This led to the import statement being printed twice. Instead, just don't print a line of it's already
            # been printed.
            lines.append(line)

    return '\n'.join(lines) + '\n'

def dict_as_function_kwarg_str(d: dict) -> str:
    lines = [_key_value_pair_to_assignment_str(key, value) for key, value in d.items()]

    return '\n\t' + ',\n\t'.join(lines) + '\n'

def _module_str_and_variable_to_import_statement(module_str: str, variable_name: str) -> str:
    return f'from {module_str} import {variable_name}'

def _key_value_pair_to_assignment_str(key: str, value: any, module_strs: List[str]=None):
    value = _assignment_output_repr(value, module_strs=module_strs)
    return f'{key} = {value}'


def _assignment_output_repr(value: any, module_strs: List[str]=None):
    """
    Main formatting function to produce executable python code
    Args:
        value: value to be assigned to a variable

    Returns:

    """
    # Handle functions, other things with builtin names
    if hasattr(value, '__name__'):
        return value.__name__

    # Handle builtins
    if _is_builtin(value):
        return _assignment_output_repr_for_builtins(value)

    # All others, try to get variable name and import
    if module_strs is not None:
        module, module_name = get_module_and_name_imported_from(value, module_strs)
        variable_name = get_imported_obj_variable_name(value, module)
    else:
        variable_name = value

    warnings.warn(f'could not find __name__ of type, and type was not builtin for {value} of type {type(value)}.'
                  f'guessed {variable_name} as value, but may not execute correctly')

    return variable_name

def _is_builtin(value: any) -> bool:
    if value is None:
        return True # None won't return True from the following check

    builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
    return type(value) in builtin_types

def _assignment_output_repr_for_builtins(value: any) -> any:
    if isinstance(value, str):
        return f"r'{value}'"

    # Other builtins, output as is
    return value



