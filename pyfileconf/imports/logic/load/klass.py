from typing import Type, Any, Dict

from pyfileconf.imports.logic.load.func import function_args_as_dict


def class_function_args_as_dict(klass: Type) -> Dict[str, Any]:
    """
    To be used on regular methods of a class e.g. ExampleClass.__init__, not on methods of an instance of the class
    """
    arg_dict = function_args_as_dict(klass.__init__)

    # TODO [#35]: handle removing first argument from __init__, may not be named self
    #
    # Current implementation depends on the argument being named self. This seems to
    # be a hard problem in general without a great solution. See
    # https://stackoverflow.com/a/47599893

    # Remove self from arguments
    arg_dict = {key: value for key, value in arg_dict.items() if key != 'self'}

    return arg_dict
