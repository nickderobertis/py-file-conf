
from dero.manager.sectionpath.sectionpath import SectionPath

def _get_from_nested_obj_by_section_path(obj, section_path: SectionPath):
    # Goes into nested sections, until it pulls the final section or pipeline
    for section in section_path:
        obj = getattr(obj, section)

    return obj


def _get_public_name_or_special_name(obj) -> str:
    for name_var in ['name', '__name__']:
        if hasattr(obj, name_var):
            return getattr(obj, name_var)

    raise ValueError(f'could not get .name or .__name__ from {obj} of type {type(obj)}')

def _has_public_name_or_special_name(obj) -> bool:
    for name_var in ['name', '__name__']:
        if hasattr(obj, name_var):
            return True

    return False