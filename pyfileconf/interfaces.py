from typing import Type, List

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
