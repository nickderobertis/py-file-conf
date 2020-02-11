from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import typing
import collections
if TYPE_CHECKING:
    from traceback import TracebackException


@dataclass
class ExampleClass:

    def __init__(self, a: Optional[typing.Tuple[int, int]] = None, name: Optional[str] = None,
                 c: Optional[collections.defaultdict] = None, d: Optional['TracebackException'] = None):
        self.a = a
        self.name = name
        self.c = c
        self.d = d

    @property
    def d(self):
        raise NotImplementedError('pipeline_manager should not access this')

    @d.setter
    def d(self, d):
        self._d = d