from typing import List
from pyfileconf.sectionpath.sectionpath import SectionPath

accepted_name_attrs = ['name', '__name__']
output_accepted_name_attrs = ['output_name'] + accepted_name_attrs

def _get_from_nested_obj_by_section_path(obj, section_path: SectionPath):
    # Goes into nested sections, until it pulls the final section or pipeline
    for section in section_path:
        obj = getattr(obj, section)

    return obj


def _get_public_name_or_special_name(obj, accept_output_names=True) -> str:
    name_attrs = _get_name_attrs(accept_output=accept_output_names)
    for name_var in name_attrs:
        if hasattr(obj, name_var):
            return getattr(obj, name_var)

    raise ValueError(f'could not get .name or .__name__ from {obj} of type {type(obj)}')

def _has_public_name_or_special_name(obj, accept_output_names=True) -> bool:
    name_attrs = _get_name_attrs(accept_output=accept_output_names)
    for name_var in name_attrs:
        if hasattr(obj, name_var):
            return True

    return False

def _get_name_attrs(accept_output: bool=True) -> List[str]:
    if accept_output:
        return output_accepted_name_attrs
    else:
        return accepted_name_attrs