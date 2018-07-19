def _is_begin_str(begin_str: str) -> bool:
    if begin_str is None:
        return False

    begin_str = begin_str.strip().lower()

    return begin_str in ('b', 'begin', 'beginning', 'start', 's')