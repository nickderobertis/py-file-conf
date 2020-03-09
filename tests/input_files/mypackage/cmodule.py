from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import typing
import collections
if TYPE_CHECKING:
    from traceback import TracebackException
import pathlib


class ExampleClass:

    def __init__(self, a: typing.Tuple[int, int], name: Optional[str] = None,
                 c: Optional[collections.defaultdict] = None, d: Optional['TracebackException'] = None,
                 f: typing.Sequence[typing.Union[collections.Counter, pathlib.Path]] =
                 (collections.Counter(), collections.Counter(), pathlib.Path('.'))):
        self.a = a
        self.name = name
        self.c = c
        self.d = d
        self.f = f

    @property
    def d(self):
        raise NotImplementedError('pipeline_manager should not access this')

    @d.setter
    def d(self, d):
        self._d = d

    @property
    def e(self):
        if self.a is None:
            raise ValueError('should only access this when a is set')
        return 10

    def __eq__(self, other):
        return all([
            self.a == other.a,
            self.name == other.name,
            self.c == other.c,
        ])