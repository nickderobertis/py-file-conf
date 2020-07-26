from pyfileconf.io.file.load.active.userdef import get_user_defined_dict_from_filepath
from pyfileconf.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader
from pyfileconf.pmcontext.actions import PyfileconfActions
from pyfileconf.pmcontext.tracing import StackTracker


class ActiveConfigFileLoader(ImportAssignmentLazyLoader):

    def load(self):
        from pyfileconf import context
        # Get ast, imports, assigns
        super().register()

        # Actually import module
        with StackTracker(file_path=self.filepath, action=PyfileconfActions.LOAD_FILE_EXECUTE):
            self._user_defined_dict = get_user_defined_dict_from_filepath(self.filepath)

        return self._user_defined_dict

    @property
    def user_defined_dict(self) -> dict:
        return self._try_getattr_else_call_func('_user_defined_dict', self.load)