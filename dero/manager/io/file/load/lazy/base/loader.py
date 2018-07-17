from dero.mixins.propertycache import SimplePropertyCacheMixin

class LazyLoader(SimplePropertyCacheMixin):

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        pass

    def register(self):
        pass

    @property
    def ast(self):
        return self._try_getattr_else_register('_ast')

    def _try_getattr_else_register(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.register)