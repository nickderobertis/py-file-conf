from typing import Union, Any, Type

from pyfileconf.imports.logic.load.klass import class_function_args_as_dict

StrOrObj = Union[str, Any]


def convert_to_empty_obj_if_necessary(item: StrOrObj, item_class: Type, key_attr: str = 'name') -> Any:
    from pyfileconf.data.models.collection import SpecificClassCollection
    if isinstance(item, (item_class, SpecificClassCollection)):
        return item

    defaults = {
        key_attr: item
    }

    args_dict = class_function_args_as_dict(item_class)
    args_dict.update(defaults)

    return item_class(**args_dict)
