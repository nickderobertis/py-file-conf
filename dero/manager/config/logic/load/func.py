from typing import Callable
import inspect


def function_args_as_dict(func: Callable):
    args = inspect.getfullargspec(func)
    out_dict = {}

    # Handle args
    num_no_default_value = _get_length_of_arg_section(args.args) - _get_length_of_arg_section(args.defaults)
    all_defaults = [None] * num_no_default_value + _get_list_of_arg_section(args.defaults)
    assert len(all_defaults) == _get_length_of_arg_section(args.args)

    for i, arg in enumerate(args.args):
        default = all_defaults[i]
        out_dict.update({arg: default})

    # Handle kwargs
    for kwarg in args.kwonlyargs:
        default = args.kwonlydefaults[kwarg] if kwarg in args.kwonlydefaults else None
        out_dict.update({kwarg: default})

    return out_dict


def _get_length_of_arg_section(section):
    if section is None:
        return 0

    return len(section)


def _get_list_of_arg_section(section):
    if section is None:
        return []

    return list(section)