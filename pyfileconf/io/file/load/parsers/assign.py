import ast
from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.assignments.models.statement import AssignmentStatement
    from pyfileconf.assignments.models.container import AssignmentStatementContainer

AssignmentStatementOrNone = Union['AssignmentStatement', None]

class AssignmentExtractor(ast.NodeVisitor):

    def __init__(self):
        from pyfileconf.assignments.models.container import AssignmentStatementContainer
        self.assigns = AssignmentStatementContainer([])

    def visit_Assign(self, node):
        from pyfileconf.assignments.models.statement import AssignmentStatement
        self.assigns.append(
            AssignmentStatement.from_ast_assign(node)
        )

    def visit_AnnAssign(self, node):
        from pyfileconf.assignments.models.statement import AssignmentStatement
        self.assigns.append(
            AssignmentStatement.from_ast_assign(node)
        )


def extract_assignments_from_ast(module: ast.Module) -> 'AssignmentStatementContainer':
    ae = AssignmentExtractor()
    ae.visit(module)
    return ae.assigns

def extract_assignment_from_ast(module: ast.Module) -> AssignmentStatementOrNone:
    assign_container = extract_assignments_from_ast(module)

    if len(assign_container) == 0:
        return None

    if len(assign_container) > 1:
        raise ValueError(f'expected to extract one assignment from ast. got {len(assign_container)} '
                         f'assigns: {assign_container.items}')

    return assign_container[0]

class AssignmentByVarnameExtractor(AssignmentExtractor):

    def __init__(self, varname: str):
        self.varname = varname
        super().__init__()

    def visit_Assign(self, node):
        varnames = [target.id for target in node.targets]
        if self.varname in varnames:
            super().visit_Assign(node)

    def visit_AnnAssign(self, node):
        if node.target.id == self.varname:
            super().visit_AnnAssign(node)


def extract_assignments_from_ast_by_name(module: ast.Module, name: str) -> 'AssignmentStatementContainer':
    ae = AssignmentByVarnameExtractor(name)
    ae.visit(module)
    return ae.assigns

def extract_assignment_from_ast_by_name(module: ast.Module, name: str) -> AssignmentStatementOrNone:
    assign_container = extract_assignments_from_ast_by_name(module, name)

    if len(assign_container) == 0:
        return None

    if len(assign_container) > 1:
        raise ValueError(f'expected to extract one assignment from ast. got {len(assign_container)} '
                         f'assigns: {assign_container.items}')

    return assign_container[0]