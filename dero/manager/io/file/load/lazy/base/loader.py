import ast
from typing import List

from dero.mixins.propertycache import SimplePropertyCacheMixin
from dero.manager.io.file.load.parsers.py import PythonFileParser
from dero.mixins.repr import ReprMixin

class LazyLoader(SimplePropertyCacheMixin, ReprMixin):
    repr_cols = ['filepath']

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        pass

    def register(self):
        self._ast, self._body = PythonFileParser(self.filepath).load()

    @property
    def ast(self) -> ast.AST:
        return self._try_getattr_else_register('_ast')

    @property
    def body(self) -> List[str]:
        return self._try_getattr_else_register('_body')

    def _try_getattr_else_register(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.register)