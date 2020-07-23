from functools import partial
from typing import Any, Dict

from pyfileconf.imports.logic.load.func import function_args_as_dict


def apply_config(obj: Any, config: dict) -> None:
    if isinstance(obj, partial):
        apply_config_to_partial(obj, config)
    else:
        apply_config_to_obj(obj, config)


def apply_config_to_obj(obj: Any, config: dict) -> None:
    attributes = dir(obj)
    init_args = function_args_as_dict(obj.__init__)
    relevant_config: Dict[str, Any] = {
        attr: value for attr, value in config.items() if attr in init_args.keys()
    }
    obj.__init__(**relevant_config)


def apply_config_to_partial(part: partial, config: dict) -> None:
    attributes = part.keywords.keys()
    for config_attr, config_item in config.items():
        # Skip irrelevant items
        if config_attr in attributes:
            part.keywords[config_attr] = config_item
