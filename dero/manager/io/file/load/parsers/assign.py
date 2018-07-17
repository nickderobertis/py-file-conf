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