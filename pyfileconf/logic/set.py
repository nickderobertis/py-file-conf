
from pyfileconf.sectionpath.sectionpath import SectionPath

def _set_in_nested_obj_by_section_path(obj, section_path: SectionPath, value) -> None:
    # Goes into nested sections, until it sets the final section or pipeline
    for section in section_path[:-1]:
        obj = getattr(obj, section)

    # Now have object of next level up from object desired to be set
    setattr(obj, section_path[-1], value)