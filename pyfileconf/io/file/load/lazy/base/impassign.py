from pyfileconf.io.file.load.lazy.base.loader import LazyLoader
from pyfileconf.io.file.load.parsers.imp import extract_imports_from_ast
from pyfileconf.io.file.load.parsers.assign import extract_assignments_from_ast
from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.imports.models.statements.container import ImportStatementContainer



class ImportAssignmentLazyLoader(LazyLoader):

    def register(self):
        # Store ast representation of file and file body
        super().register()

        # Store imports and assignments
        if self._ast is not None:
            self._imports = extract_imports_from_ast(self._ast)
            self._assigns = extract_assignments_from_ast(self._ast)
        else:
            self._imports = ImportStatementContainer([])
            self._assigns = AssignmentStatementContainer([])

    @property
    def imports(self) -> ImportStatementContainer:
        return self._try_getattr_else_register('_imports')

    @property
    def assigns(self) -> AssignmentStatementContainer:
        return self._try_getattr_else_register('_assigns')