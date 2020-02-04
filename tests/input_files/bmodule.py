from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ExampleClass:

    def __init__(self, a: Optional[Tuple[int, int]] = None, name: Optional[str] = None):
        self.a = a
        self.name = name
