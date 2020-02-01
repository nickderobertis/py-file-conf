from typing import Callable, Any
import inspect


def function_args_as_dict(func: Callable):
    args = inspect.getfullargspec(func)
    out_dict = {}

    # for methods and classmethods, want to ignore the first argument (self, cls)
    if inspect.ismethod(func):
        del args.args[0] # delete self arg

    # Handle args
    num_no_default_value = _get_length_of_arg_section(args.args) - _get_length_of_arg_section(args.defaults)
    all_defaults = [None] * num_no_default_value + _get_list_of_arg_section(args.defaults)
    assert len(all_defaults) == _get_length_of_arg_section(args.args)

    for i, arg in enumerate(args.args):
        default = all_defaults[i]
        out_dict.update({arg: default})

    # Handle kwargs
    for kwarg in args.kwonlyargs:
        if args.kwonlydefaults:
            default = args.kwonlydefaults[kwarg] if kwarg in args.kwonlydefaults else None
            out_dict.update({kwarg: default})

    return out_dict


def get_variable_name_of_obj(obj: Any) -> str:
    return [key for key, value in globals().items() if value == obj][0]


def _get_length_of_arg_section(section):
    if section is None:
        return 0

    return len(section)


def _get_list_of_arg_section(section):
    if section is None:
        return []

    return list(section)