from dataclasses import dataclass
from typing import List, Tuple, Optional

from tests.input_files.bmodule import ExampleClass


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

