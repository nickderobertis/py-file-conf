from dataclasses import dataclass
from functools import wraps
from typing import List, Tuple, Optional, Union, Sequence, Iterable, Any, Dict

from pyfileconf import IterativeRunner
from pyfileconf.runner.models.interfaces import IterativeResults
from pyfileconf.selector.models.itemview import ItemView
from tests.input_files.mypackage.cmodule import ExampleClass

# TODO [#102]: better support for decorated functions
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


def a_function_that_calls_iterative_runner(to_run: List[Union[str, ItemView]],
                                           cases: Sequence[Dict[str, Any]],
                                           ec: ExampleClass) -> IterativeResults:
    """
    An example function which calls IterativeRunner
    """
    runner = IterativeRunner(to_run, cases)
    runner._run()  # sets config dependencies
    results = runner.run()

    # access attribute of another config
    ec.a

    return results


@dataclass
class SecondExampleClass:

    def __init__(self, b: ExampleClass = None, name: Optional[str] = None):
        self.b = b
        self.name = name

