import ast
from typing import Optional, Union

import black

from pyfileconf.sectionpath.sectionpath import SectionPath


def add_item_into_nested_dict_at_section_path(nested_dict: dict, section_path: SectionPath, item: str,
                                              add_as_ast_name: bool = True):
    """
    :Notes:
        Inplace

    :param nested_dict:
    :param section_path:
    :param item:
    :return:
    """
    current_dict = nested_dict
    for i, section in enumerate(section_path):
        if i <= len(section_path) - 2:
            # Up until the next to last item, pull out the nested dicts, creating if necessary
            try:
                current_dict = current_dict[section]
                # Section already exists, keep navigating deeper
            except KeyError:
                # Section does not yet exist, create it, then navigate into it
                current_dict[section] = {}
                current_dict = current_dict[section]
        if i == len(section_path) - 1:
            # Reached final section. Because we only went up until the next to last item pulling out
            # nested dicts, current_dict should now be the dict which contains the container for
            # the item to be stored.

            # Need to create entry in this section.
            new_entry: Union[str, ast.Name]
            if add_as_ast_name:
                new_entry = ast.Name(item)
            else:
                new_entry = item

            # First see if there is already an existing section
            try:
                last_container = current_dict[section]
            except KeyError:
                # No last section, create it
                current_dict[section] = []
                last_container = current_dict[section]

            if not isinstance(last_container, list):
                raise ValueError('trying to insert item into existing dictionary section, must be existing '
                                 'list section or non-existent section')

            last_container.append(new_entry)


def create_dict_assignment_str_from_nested_dict_with_ast_names(nested_dict: dict, existing_str: Optional[str] = None,
                                                               assign_to_name: str = 'pipeline_dict') -> str:
    if existing_str is None:
        use_str = f'{assign_to_name} = {{'
    else:
        use_str = ''

    for key, value in nested_dict.items():
        use_str += f'"{key}": '
        if isinstance(value, ast.Name):
            use_str += value.id + ','
        elif isinstance(value, str):
            use_str += value + ','
        elif isinstance(value, list):
            use_str += '['
            for item in value:
                use_str += item.id + ','
            use_str += '],'
        elif isinstance(value, dict):
            use_str += '{'
            use_str += create_dict_assignment_str_from_nested_dict_with_ast_names(value, use_str)
            use_str += '},'
        else:
            raise ValueError(f'could not parse object {value} of type {type(value)} in '
                             f'creating pipeline dict str')

    if existing_str is None:
        # Must be finishing top-level operation, finish str
        use_str += '}'
        # Pretty print the string using black formatter
        use_str = pretty_format_str(use_str)

    return use_str


def pretty_format_str(string: str) -> str:
    fm = black.FileMode()
    out_str = black.format_str(string, mode=fm)
    return out_str