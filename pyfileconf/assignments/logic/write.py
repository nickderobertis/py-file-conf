from typing import List, Any, cast

from pyfileconf.imports.logic.load.name import get_module_and_name_imported_from, get_imported_obj_variable_name
from pyfileconf.logic.inspect import _is_builtin


def _key_value_pair_to_assignment_str(key: str, value: Any, module_strs: List[str] = None):
    value = _assignment_output_repr(value, module_strs=module_strs)
    return f'{key} = {value}'


def _assignment_output_repr(value: Any, module_strs: List[str] = None):
    """
    Main formatting function to produce executable python code
    Args:
        value: value to be assigned to a variable

    Returns:

    """
    from pyfileconf.selector.models.selector import _is_selector
    from pyfileconf.selector.models.itemview import _is_item_view, ItemView
    if _is_selector(value):
        # accessing porperties of selector object will cause issues. Only need to return Selector()
        return 'Selector()'

    if _is_item_view(value):
        # accessing properties of ItemView object will also cause issues. need to return s. and section path
        return f's.{value.section_path_str}'

    # Handle functions, other things with builtin names
    try:
        return value.__name__
    except (AttributeError, KeyError):
        pass

    # Handle builtins
    if _is_builtin(value):
        return _assignment_output_repr_for_builtins(value)

    # All others, try to get variable name and import
    if module_strs is not None:
        module_and_module_name_or_none = get_module_and_name_imported_from(value, module_strs)
        if module_and_module_name_or_none is None:
            # warnings.warn(f'could not find import module for {value}\n will generate assignment statement. '
            #               f'likely, the configuration file will need to be manually updated.')
            return None

        module, module_name = module_and_module_name_or_none
        variable_name = get_imported_obj_variable_name(value, module)
    else:
        variable_name = value

    # warnings.warn(f'could not find __name__ of type, and type was not builtin for {value} of type {type(value)}.'
    #               f'guessed {variable_name} as value, but may not execute correctly')

    return variable_name


def _assignment_output_repr_for_builtins(value: Any) -> Any:
    if isinstance(value, str):
        return f"r'{value}'"

    # Other builtins, output as is
    return value