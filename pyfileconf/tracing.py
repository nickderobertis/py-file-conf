from typing import Optional

from pyfileconf.sectionpath.sectionpath import SectionPath


class RunningTracker:
    orig_running_section_path_str: Optional[str]

    def __init__(self, section_path_str: str, base_section_path_str: Optional[str] = None):
        if base_section_path_str is not None:
            new_sp = SectionPath.join(base_section_path_str, section_path_str)
            section_path_str = new_sp.path_str
        self.section_path_str = section_path_str
        self.orig_running_section_path_str = None

    def __enter__(self):
        from pyfileconf import context
        self.orig_running_section_path_str = context.currently_running_section_path_str
        context.currently_running_section_path_str = self.section_path_str

    def __exit__(self, exc_type, exc_val, exc_tb):
        from pyfileconf import context
        context.currently_running_section_path_str = self.orig_running_section_path_str
