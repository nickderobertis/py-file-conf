
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer


class FileStr:

    def __init__(self, import_assignment_obj, existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer):
        """

        Args:
            import_assignment_obj: object which has method obj.as_imports_and_assignments()
            existing_imports:
            existing_assigns:
        """
        self.file_str = self._create_str(
            import_assignment_obj=import_assignment_obj,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns
        )

    def _create_str(self, import_assignment_obj, existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer):
        """
        calls obj.as_imports_and_assignments(), combines those with existing imports and
        assignments

        Args:
            import_assignment_obj:
            existing_imports:
            existing_assigns:

        Returns:

        """
        pass