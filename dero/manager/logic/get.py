
from dero.manager.sectionpath.sectionpath import SectionPath

def _get_from_nested_obj_by_section_path(obj, section_path: SectionPath):
    # Goes into nested sections, until it pulls the final section or pipeline
    for section in section_path:
        obj = getattr(obj, section)

    return obj