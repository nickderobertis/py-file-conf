from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ExampleClass:

    def __init__(self, a: Tuple[int, int]):
        self.a = a

