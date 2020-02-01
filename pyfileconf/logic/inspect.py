import builtins
from typing import Any


def _is_builtin(value: Any) -> bool:
    if value is None:
        return True # None won't return True from the following check

    builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
    return type(value) in builtin_types

def _is_str_matching_builtin_type(str_value: str) -> bool:
    """
    should pass 'str', 'int', etc.
    """
    builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
    return f"<class '{str_value}'>" in [str(bt) for bt in builtin_types]