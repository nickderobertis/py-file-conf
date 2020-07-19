from typing import Any


def combine_items_into_list_whether_they_are_lists_or_not_then_extract_from_list_if_only_one_item(
    item1: Any, item2: Any
) -> Any:
    items = combine_items_into_list_whether_they_are_lists_or_not(item1, item2)
    if len(items) == 1:
        return items[0]

    return items


def combine_items_into_list_whether_they_are_lists_or_not(
    item1: Any, item2: Any
) -> list:
    item1_list = _to_list(item1)
    item2_list = _to_list(item2)
    return [*item1_list, *item2_list]


def _to_list(item: Any) -> list:
    if item is None:
        return []
    if isinstance(item, list):
        return item
    elif isinstance(item, tuple):
        return list(item)
    else:
        return [item]
