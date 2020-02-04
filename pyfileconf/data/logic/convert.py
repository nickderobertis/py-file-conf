from typing import Union, Any, Type

from pyfileconf.data.models.source import DataSource

StrOrObj = Union[str, Any]

def convert_to_empty_obj_if_necessary(item: StrOrObj, item_class: Type) -> DataSource:
    from pyfileconf.data.models.collection import SpecificClassCollection
    if isinstance(item, (item_class, SpecificClassCollection)):
        return item

    return item_class(name=item)