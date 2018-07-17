from typing import Tuple, List

from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer

ImportsAssignsTuple = Tuple[ImportStatementContainer, AssignmentStatementContainer]

class FileStr:

    def __init__(self, import_assignment_obj, existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer, existing_body: List[str]):
        """

        Args:
            import_assignment_obj: object which has method obj.as_imports_and_assignments()
            existing_imports:
            existing_assigns:
            existing_body: should not contain imports, but should contain rest of existing file as str
        """
        self.file_str = self._create_str(
            import_assignment_obj=import_assignment_obj,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns,
            existing_body=existing_body
        )

    def _create_str(self, import_assignment_obj, existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer, existing_body: List[str]) -> str:
        """
        calls obj.as_imports_and_assignments(), combines those with existing imports and
        assignments

        Args:
            import_assignment_obj:
            existing_imports:
            existing_assigns:

        Returns:

        """
        all_imports, new_assigns = self._combine_imports_get_new_assignments(
            import_assignment_obj,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns
        )

        # Now convert to str
        items = [
            str(all_imports),
            ''.join(existing_body),
            str(new_assigns)
        ]
        valid_items = [item for item in items if item not in ('', None)]
        return '\n'.join(valid_items)

    def _combine_imports_get_new_assignments(self, import_assignment_obj, existing_imports: ImportStatementContainer,
                                             existing_assigns: AssignmentStatementContainer) -> ImportsAssignsTuple:
        all_imports = existing_imports.copy()
        new_assigns = AssignmentStatementContainer([])

        possibly_new_imports, possibly_new_assigns = import_assignment_obj.as_imports_and_assignments()

        for imp in possibly_new_imports:
            if imp not in all_imports:
                all_imports.append(imp)

        for assign in possibly_new_assigns:
            if assign not in existing_assigns:
                new_assigns.append(assign)

        return all_imports, new_assigns
