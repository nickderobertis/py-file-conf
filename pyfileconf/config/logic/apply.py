from functools import partial
from typing import Any


def apply_config(obj: Any, config: dict) -> None:
    if isinstance(obj, partial):
        apply_config_to_partial(obj, config)
    else:
        apply_config_to_obj(obj, config)


def apply_config_to_obj(obj: Any, config: dict) -> None:
    attributes = dir(obj)
    for config_attr, config_item in config.items():
        # Skip irrelevant items
        if config_attr in attributes:
            setattr(obj, config_attr, config_item)


def apply_config_to_partial(part: partial, config: dict) -> None:
    attributes = part.keywords.keys()
    for config_attr, config_item in config.items():
        # Skip irrelevant items
        if config_attr in attributes:
            part.keywords[config_attr] = config_item
