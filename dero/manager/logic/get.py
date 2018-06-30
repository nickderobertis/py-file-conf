
from dero.manager.sectionpath.sectionpath import SectionPath

def _get_from_nested_obj_by_section_path(obj, section_path: SectionPath):
    # Goes into nested sections, until it pulls the final section or pipeline
    for section in section_path:
        obj = getattr(obj, section)

    return obj


def _get_public_name_or_special_name(obj):
    if hasattr(obj, 'name'):
        return obj.name

    if hasattr(obj, '__name__'):
        return obj.__name__

    raise ValueError(f'could not get .name or .__name__ from {obj} of type {type(obj)}')