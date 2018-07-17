import ast

from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.assignments.models.container import AssignmentStatementContainer


class AssignmentExtractor(ast.NodeVisitor):

    def __init__(self):
        self.assigns = AssignmentStatementContainer([])

    def visit_Assign(self, node):
        self.assigns.append(
            AssignmentStatement.from_ast_assign(node)
        )

    def visit_AnnAssign(self, node):
        self.assigns.append(
            AssignmentStatement.from_ast_assign(node)
        )


def extract_assignments_from_ast(module: ast.Module) -> AssignmentStatementContainer:
    ae = AssignmentExtractor()
    ae.visit(module)
    return ae.assigns

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


def extract_assignments_from_ast_by_name(module: ast.Module, name: str) -> AssignmentStatementContainer:
    ae = AssignmentByVarnameExtractor(name)
    ae.visit(module)
    return ae.assigns