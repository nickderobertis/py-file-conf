from pyfileconf.io.file.load.active.userdef import get_user_defined_dict_from_filepath
from pyfileconf.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader

class ActiveConfigFileLoader(ImportAssignmentLazyLoader):

    def load(self):
        from pyfileconf import context
        # Get ast, imports, assigns
        super().register()

        # Actually import module
        context.file_is_currently_being_loaded = True
        self._user_defined_dict = get_user_defined_dict_from_filepath(self.filepath)
        context.file_is_currently_being_loaded = False

        return self._user_defined_dict

    @property
    def user_defined_dict(self) -> dict:
        return self._try_getattr_else_call_func('_user_defined_dict', self.load)