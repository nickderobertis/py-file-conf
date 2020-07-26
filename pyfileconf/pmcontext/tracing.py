from typing import Optional

from pyfileconf.pmcontext.actions import PyfileconfActions
from pyfileconf.pmcontext.stack import PyfileconfFrame
from pyfileconf.sectionpath.sectionpath import SectionPath


class StackTracker:
    def __init__(
        self,
        section_path_str: Optional[str] = None,
        action: PyfileconfActions = PyfileconfActions.RUN,
        file_path: Optional[str] = None,
        base_section_path_str: Optional[str] = None,
    ):
        if section_path_str is None and file_path is None:
            raise ValueError("must provide one of section_path_str or file_path")

        if base_section_path_str is not None:
            new_sp = SectionPath.join(base_section_path_str, section_path_str)
            section_path_str = new_sp.path_str
        self.section_path_str = section_path_str
        self.action = action
        self.file_path = file_path

    def _get_frame(self):
        if self.section_path_str is None:
            return PyfileconfFrame.from_file_path(self.file_path, action=self.action)
        else:
            return PyfileconfFrame(
                self.section_path_str, self.action, file_path=self.file_path
            )

    def __enter__(self):
        from pyfileconf import context

        frame = self._get_frame()
        context.stack.add_frame(frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        from pyfileconf import context

        context.stack.pop_frame()
