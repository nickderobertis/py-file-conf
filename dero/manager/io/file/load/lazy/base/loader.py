import ast

from dero.mixins.propertycache import SimplePropertyCacheMixin
from dero.manager.io.file.load.parsers.py import PythonFileParser

class LazyLoader(SimplePropertyCacheMixin):

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        pass

    def register(self):
        self._ast = PythonFileParser(self.filepath).load()

    @property
    def ast(self) -> ast.AST:
        return self._try_getattr_else_register('_ast')

    def _try_getattr_else_register(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.register)