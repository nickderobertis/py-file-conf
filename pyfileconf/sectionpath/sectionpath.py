from typing import List, Union, TYPE_CHECKING, Sequence, Optional, cast

if TYPE_CHECKING:
    from pyfileconf.selector.models.itemview import ItemView
import os

from mixins.repr import ReprMixin

SectionPathOrStr = Union[str, 'SectionPath']

class SectionPath(ReprMixin):
    repr_cols = ['path_str', 'sections']

    def __init__(self, section_path: str):
        self.path_str = section_path
        self.sections = _section_path_str_to_section_strs(section_path)

    def __iter__(self):
        for section in self.sections:
            yield section

    def __getitem__(self, item):
        return self.sections[item]

    def __len__(self):
        return len(self.sections)

    @classmethod
    def from_filepath(cls, basepath: str, filepath: str):
        relative_path = os.path.relpath(filepath, start=basepath)
        section_path = _relative_filepath_to_section_path(relative_path)
        return cls(section_path)

    @classmethod
    def from_section_str_list(cls, section_strs: List[str]):
        section_path = _section_strs_to_section_path_str(section_strs)
        return cls(section_path)

    @classmethod
    def from_ambiguous(cls, item: Union[str, 'ItemView', 'SectionPath'], strip_manager_from_iv: bool = False):
        from pyfileconf.selector.models.itemview import _is_item_view
        if _is_item_view(item):
            item = cast('ItemView', item)
            sp = cls(item.section_path_str)
            if strip_manager_from_iv:
                relative_section_path = cls.from_section_str_list(sp[1:])
                return relative_section_path
            else:
                return sp
        if isinstance(item, cls):
            return item
        if isinstance(item, str):
            return cls(item)
        raise ValueError(f'cannot parse {item} of type {item} to create SectionPath')

    @classmethod
    def list_from_ambiguous(
        cls,
        items: Union[str, 'ItemView', 'SectionPath', Sequence[Union[str, 'ItemView', 'SectionPath']]],
        base_section_path_str: Optional[str] = None,
        strip_manager_from_iv: bool = False
    ) -> List['SectionPath']:
        if isinstance(items, (list, tuple)):
            items_list = items
        else:
            items = cast(Union[str, 'ItemView', 'SectionPath'], items)
            items_list = [items]

        sp_results: List[SectionPath] = []
        for item in items_list:
            sp = SectionPath.from_ambiguous(item, strip_manager_from_iv=strip_manager_from_iv)
            if base_section_path_str is not None:
                sp = SectionPath.join(base_section_path_str, sp)
            sp_results.append(sp)

        return sp_results

    @classmethod
    def join(cls, section_path_1: SectionPathOrStr, section_path_2: SectionPathOrStr):
        section_path_1 = _convert_to_section_path_if_necessary(section_path_1)
        section_path_2 = _convert_to_section_path_if_necessary(section_path_2)

        output_path_sections = section_path_1.sections + section_path_2.sections
        return cls.from_section_str_list(output_path_sections)

    def to_filepath(self, basepath: str):
        relative_path = _section_path_to_relative_filepath(self)
        return os.path.join(basepath, relative_path)

    def endswith(self, sp: 'SectionPath'):
        num_to_match = len(sp)
        match_parts = self[-num_to_match:]
        for i, part in enumerate(match_parts):
            if part != sp[i]:
                return False
        return True

    def __eq__(self, other):
        try:
            return self.path_str == other.path_str
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.path_str)


def _section_path_str_to_section_strs(section_path_str: str) -> List[str]:
    return section_path_str.split('.')

def _section_strs_to_section_path_str(section_strs: List[str]) -> str:
    return '.'.join(section_strs)

def _relative_filepath_to_section_path(filepath: str) -> str:
    sections = filepath.split(os.path.sep)
    sections[-1] = _strip_py(sections[-1]) # remove .py if exists at end of filepath
    return _section_strs_to_section_path_str(sections)

def _section_path_to_relative_filepath(section_path: SectionPath) -> str:
    return os.path.sep.join(section_path.sections)

def _strip_py(filename_str: str) -> str:
    if not filename_str.endswith('.py'):
        return filename_str

    return filename_str[:-3]

def _convert_to_section_path_if_necessary(section_path: SectionPathOrStr) -> SectionPath:
    if isinstance(section_path, SectionPath):
        return section_path
    elif isinstance(section_path, str):
        return SectionPath(section_path)
    else:
        raise ValueError(f'expected SectionPath or str. got {section_path} of type {type(section_path)}')