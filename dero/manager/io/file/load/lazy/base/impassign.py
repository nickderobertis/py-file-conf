from dero.manager.io.file.load.lazy.base.loader import LazyLoader


class ImportAssignmentLazyLoader(LazyLoader):

    def register(self):
        # Store ast representation of file
        super().register()

        # Store imports and assignments

    @property
    def imports(self):
        return self._try_getattr_else_register('_imports')

    @property
    def assigns(self):
        return self._try_getattr_else_register('_assigns')