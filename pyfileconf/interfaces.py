from typing import Type, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pyfileconf.selector.models.itemview import ItemView
    from pyfileconf.sectionpath.sectionpath import SectionPath

from typing_extensions import TypedDict


SpecificClassConfigDict = TypedDict(
    "SpecificClassConfigDict",
    {
        "name": str,
        "class": Type,
        "always_import_strs": List[str],
        "always_assign_strs": List[str],
        "key_attr": str,
        "execute_attr": str,
    },
    total=False
)

SectionPathLike = Union[str, 'ItemView', 'SectionPath']
