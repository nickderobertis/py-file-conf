from typing import Optional

from pyfileconf.pmcontext.actions import PyfileconfActions
from pyfileconf.pmcontext.stack import PyfileconfFrame
from pyfileconf.sectionpath.sectionpath import SectionPath


class StackTracker:

    def __init__(self, section_path_str: str, action: PyfileconfActions = PyfileconfActions.RUN,
                 base_section_path_str: Optional[str] = None):
        if base_section_path_str is not None:
            new_sp = SectionPath.join(base_section_path_str, section_path_str)
            section_path_str = new_sp.path_str
        self.section_path_str = section_path_str
        self.action = action

    def __enter__(self):
        from pyfileconf import context
        frame = PyfileconfFrame(self.section_path_str, self.action)
        context.stack.add_frame(frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        from pyfileconf import context
        context.stack.pop_frame()
