import builtins
from typing import Any
import inspect
from types import FrameType
from typing import cast


def get_caller_frame() -> FrameType:
    """Return the calling function's name."""
    return cast(FrameType, cast(FrameType, inspect.currentframe()).f_back)


def get_caller_filepath(caller_levels: int = 2) -> str:
    this_frame = get_caller_frame()
    frame = this_frame
    for _ in range(caller_levels):
        frame = frame.f_back
    return frame.f_code.co_filename


def _is_builtin(value: Any) -> bool:
    if value is None:
        return True  # None won't return True from the following check

    builtin_types = [
        getattr(builtins, d)
        for d in dir(builtins)
        if isinstance(getattr(builtins, d), type)
    ]
    return type(value) in builtin_types


def _is_str_matching_builtin_type(str_value: str) -> bool:
    """
    should pass 'str', 'int', etc.
    """
    builtin_types = [
        getattr(builtins, d)
        for d in dir(builtins)
        if isinstance(getattr(builtins, d), type)
    ]
    return f"<class '{str_value}'>" in [str(bt) for bt in builtin_types]
