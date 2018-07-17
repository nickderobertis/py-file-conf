import ast

from dero.manager.imports.models.statements.interfaces import ObjectImportStatement, ModuleImportStatement
from dero.manager.imports.models.statements.container import ImportStatementContainer

class ImportExtractor(ast.NodeVisitor):

    def __init__(self):
        self.imports = ImportStatementContainer([])

    def visit_Import(self, node):
        self.imports.append(
            ModuleImportStatement.from_ast_import(node)
        )

    def visit_ImportFrom(self, node):
        self.imports.append(
            ObjectImportStatement.from_ast_import_from(node)
        )

def extract_imports_from_ast(module: ast.Module) -> ImportStatementContainer:
    ie = ImportExtractor()
    ie.visit(module)
    return ie.imports