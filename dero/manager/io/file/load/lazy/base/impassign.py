from dero.manager.io.file.load.lazy.base.loader import LazyLoader
from dero.manager.io.file.load.parsers.imp import extract_imports_from_ast
from dero.manager.io.file.load.parsers.assign import extract_assignments_from_ast
from dero.manager.assignments.models.container import AssignmentStatementContainer
from dero.manager.imports.models.statements.container import ImportStatementContainer



class ImportAssignmentLazyLoader(LazyLoader):

    def register(self):
        # Store ast representation of file and file body
        super().register()

        # Store imports and assignments
        self._imports = extract_imports_from_ast(self._ast)
        self._assigns = extract_assignments_from_ast(self._ast)

    @property
    def imports(self) -> ImportStatementContainer:
        return self._try_getattr_else_register('_imports')

    @property
    def assigns(self) -> AssignmentStatementContainer:
        return self._try_getattr_else_register('_assigns')