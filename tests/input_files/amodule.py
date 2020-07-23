from dataclasses import dataclass
from functools import wraps
from typing import List, Tuple, Optional

from tests.input_files.mypackage.cmodule import ExampleClass

# TODO: better support for decorated functions
#
# The argument introspection breaks if *args, **kwargs
# is used in the decorator as it can no longer detect
# the original call signature. It should detect that it
# has received a decorated function and extract the
# call signature from the original function. But need to
# consider cases where the decorator actually could change
# the call signature. Need to also experiment with the
# different methods of creating decorators.
def track_a_function_in_example_class(f):
    @wraps(f)
    # Changing this call signature to *args, **kwargs breaks pyfileconf
    def wrapper(a: ExampleClass, b: List[str]):
         ExampleClass._a_function_instances[id(f)] = f
         return f(a, b)
    return wrapper


@track_a_function_in_example_class
def a_function(a: ExampleClass, b: List[str]) -> Tuple[ExampleClass, List[str]]:
    """
    An example function
    """
    return a, b


@dataclass
class SecondExampleClass:

    def __init__(self, b: ExampleClass = None, name: Optional[str] = None):
        self.b = b
        self.name = name

