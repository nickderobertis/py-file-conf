from dataclasses import dataclass
from typing import Optional, Tuple
import typing
import collections


@dataclass
class ExampleClass:

    def __init__(self, a: Optional[typing.Tuple[int, int]] = None, name: Optional[str] = None,
                 c: Optional[collections.defaultdict] = None):
        self.a = a
        self.name = name
        self.c = c