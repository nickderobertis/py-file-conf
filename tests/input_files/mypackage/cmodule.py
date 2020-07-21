from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
import typing
import collections

from pyfileconf import Selector

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

    def __call__(self, *args, **kwargs):
        return 'woo'

    def my_call(self):
        return 'woo2'

    def dependent_call(self):
        from pyfileconf import context
        # Get active pipeline manager
        assert len(context.active_managers) == 1
        manager = list(context.active_managers.values())[0]

        s = Selector()
        # Specific classes
        # Access ItemView - should not be dependency
        obj = s.test_pipeline_manager.example_class.stuff.data2
        # Access attr
        a = s.test_pipeline_manager.example_class.stuff.data3.a

        # Classes
        # Call ItemView
        b = s.test_pipeline_manager.ec.ExampleClass()
        # Get by PM
        c = manager.get(s.test_pipeline_manager.ec2.ExampleClass)
        # Access ItemView - should not be dependency
        f = s.test_pipeline_manager.ec3.ExampleClass

        # Functions
        # Call function
        d = s.test_pipeline_manager.af.a_function()
        # Run by PM
        e = manager.run(s.test_pipeline_manager.af2.a_function)
        # Access ItemView - should not be dependency
        g = s.test_pipeline_manager.af3.a_function
        return obj, a, b, c, d, e, f, g

    def dependent_call_with_context_update(self):
        from pyfileconf import context
        context.currently_running_section_path_str = 'test_pipeline_manager.example_class.stuff.data4'
        return self.dependent_call()

