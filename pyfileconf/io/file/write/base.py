from typing import Tuple, List

from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.assignments.models.container import AssignmentStatementContainer

ImportsDoubleAssignsTuple = Tuple[ImportStatementContainer, AssignmentStatementContainer, AssignmentStatementContainer]

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
        all_imports, new_assigns_begin, new_assigns_end = self._combine_imports_get_new_assignments(
            import_assignment_obj,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns
        )

        # Now convert to str
        items = [
            str(all_imports) + '\n',
            str(new_assigns_begin),
            '\n'.join(existing_body),
            str(new_assigns_end)
        ]
        valid_items = [item for item in items if item not in ('', None)]
        return '\n'.join(valid_items)

    def _combine_imports_get_new_assignments(self, import_assignment_obj,
                                        existing_imports: ImportStatementContainer,
                                        existing_assigns: AssignmentStatementContainer) -> ImportsDoubleAssignsTuple:
        all_imports = existing_imports.copy()
        new_assigns_begin = AssignmentStatementContainer([])
        new_assigns_end = AssignmentStatementContainer([])

        possibly_new_imports, possibly_new_assigns = import_assignment_obj.as_imports_and_assignments()

        # Checks to see whether should be added, and whether to beginning or end, then adds
        [all_imports.add_if_missing(imp) for imp in possibly_new_imports]

        for assign in possibly_new_assigns:
            if not existing_assigns.contains_varname(assign.varname):
                begin = getattr(assign, 'prefer_beginning', False)
                if begin:
                    new_assigns_begin.append_if_missing(assign)
                else:
                    new_assigns_end.append_if_missing(assign)

        return all_imports, new_assigns_begin, new_assigns_end
