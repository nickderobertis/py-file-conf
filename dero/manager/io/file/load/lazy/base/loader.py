
class LazyLoader:

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
        return self._try_getattr_else_call_method_by_str(attr, 'register')

    def _try_getattr_else_call_method_by_str(self, attr: str, method_str: str):
        try:
            return getattr(self, attr)
        except AttributeError:
            method = getattr(self, method_str)
            method()

        return getattr(self, attr)