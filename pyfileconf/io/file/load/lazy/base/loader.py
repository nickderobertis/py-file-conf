from ast import AST
import os
from typing import List

from mixins.propertycache import SimplePropertyCacheMixin
from pyfileconf.io.file.load.parsers.py import PythonFileParser
from mixins.repr import ReprMixin

class LazyLoader(SimplePropertyCacheMixin, ReprMixin):
    repr_cols = ['filepath']

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        pass

    def register(self):
        if os.path.exists(self.filepath):
            self._ast, self._body = PythonFileParser(self.filepath).load()
        else:
            self._ast, self._body = None, None

    @property
    def ast(self) -> AST:
        return self._try_getattr_else_register('_ast')

    @property
    def body(self) -> List[str]:
        return self._try_getattr_else_register('_body')

    def _try_getattr_else_register(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.register)