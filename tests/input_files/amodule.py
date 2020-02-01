from typing import List, Tuple

from tests.input_files.bmodule import ExampleClass


def a_function(a: ExampleClass, b: List[str]) -> Tuple[ExampleClass, List[str]]:
    """
    An example function
    """
    return a, b
