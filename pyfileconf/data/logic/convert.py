from typing import Union, Any, Type

StrOrObj = Union[str, Any]


def convert_to_empty_obj_if_necessary(item: StrOrObj, item_class: Type, key_attr: str = 'name') -> Any:
    from pyfileconf.data.models.collection import SpecificClassCollection
    if isinstance(item, (item_class, SpecificClassCollection)):
        return item

    defaults = {
        key_attr: item
    }

    return item_class(**defaults)
