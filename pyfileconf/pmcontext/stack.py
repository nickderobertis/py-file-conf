from typing import Sequence, List, Union, TYPE_CHECKING, Optional

from mixins.repr import ReprMixin

from pyfileconf.interfaces import SectionPathLike

from pyfileconf.pmcontext.actions import PyfileconfActions


class PyfileconfFrame:

    def __init__(self, section_path: SectionPathLike, action: PyfileconfActions):
        from pyfileconf.sectionpath.sectionpath import SectionPath
        self.section_path = SectionPath.from_ambiguous(section_path)
        self.action = action

    def __repr__(self):
        return f'<PyfileconfFrame(section_path={self.section_path.path_str}, action={self.action.value})>'


class PyfileconfStack:
    frames: List[PyfileconfFrame]

    def __init__(self, frames: Sequence[PyfileconfFrame]):
        self.frames = list(frames)

    def __getitem__(self, item):
        return self.frames[item]

    def __repr__(self):
        frame_repr = '\n'.join(f'{i}\t{repr(frame)}' for i, frame in enumerate(self))
        return f'<PyfileconfStack(\n{frame_repr}\n)>'

    def add_frame(self, frame: PyfileconfFrame):
        self.frames.append(frame)

    def pop_frame(self) -> PyfileconfFrame:
        return self.frames.pop(-1)

    def add_running_item(self, section_path: SectionPathLike):
        frame = PyfileconfFrame(section_path, PyfileconfActions.RUN)
        self.add_frame(frame)

    @property
    def currently_running_section_path_str(self) -> Optional[str]:
        run_frames = [frame for frame in self if frame.action == PyfileconfActions.RUN]
        if not run_frames:
            return None

        return run_frames[-1].section_path.path_str
