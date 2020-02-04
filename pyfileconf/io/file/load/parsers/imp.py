import ast
from typing import Union

from pyfileconf.exceptions.imports import ExtractedIncorrectTypeOfImportException
from pyfileconf.imports.models.statements.interfaces import (
    ObjectImportStatement,
    ModuleImportStatement,
    AnyImportStatement
)
from pyfileconf.imports.models.statements.container import ImportStatementContainer

AnyImportStatementOrNone = Union[AnyImportStatement, None]
ObjectImportStatementOrNone = Union[ObjectImportStatement, None]
ModuleImportStatementOrNone = Union[ModuleImportStatement, None]

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

def extract_obj_import_from_ast(module: ast.Module) -> ObjectImportStatementOrNone:
    import_container = extract_imports_from_ast(module)
    imp = _extract_single_import_from_container(import_container)
    _validate_import_type(imp, ObjectImportStatement)

    return imp

def extract_module_import_from_ast(module: ast.Module) -> ModuleImportStatementOrNone:
    import_container = extract_imports_from_ast(module)
    imp = _extract_single_import_from_container(import_container)
    _validate_import_type(imp, ModuleImportStatement)

    return imp

def _extract_single_import_from_container(import_container: ImportStatementContainer) -> AnyImportStatementOrNone:
    if len(import_container) == 0:
        return None

    if len(import_container) > 1:
        raise ValueError(f'expected to extract one import, got {len(import_container)} imports: '
                         f'{import_container.items}')

    return import_container[0]

def _validate_import_type(import_statement: AnyImportStatementOrNone, enforce_type: type=ObjectImportStatement):
    if import_statement is None:
        return

    if not isinstance(import_statement, enforce_type):
        raise ExtractedIncorrectTypeOfImportException(
            f'expected import of type {enforce_type}, got {import_statement} of '
            f'type {type(import_statement)}'
        )