from pyfileconf.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader
from pyfileconf.io.file.load.parsers.assign import extract_assignment_from_ast_by_name
from pyfileconf.pmcontext.actions import PyfileconfActions
from pyfileconf.pmcontext.tracing import StackTracker


class SpecificClassDictAstLoader(ImportAssignmentLazyLoader):

    def load(self):
        # Get ast, imports, assigns
        super().register()

        with StackTracker(file_path=self.filepath, action=PyfileconfActions.LOAD_PIPELINE_FILE_AST):
            # Store pipeline dict assignment
            self._class_dict_assign = extract_assignment_from_ast_by_name(self._ast, 'class_dict')

    @property
    def class_dict_assign(self):
        return self._try_getattr_else_load('_class_dict_assign')

    def _try_getattr_else_load(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.load)