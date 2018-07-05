from typing import List

from dero.manager.imports.logic.parse.combine import combine_imports_lines_into_import_statements
from dero.manager.imports.logic.parse.clean import pre_process_import_statement_get_renames
from dero.manager.imports.logic.parse.classify import is_module_import, is_obj_import
from dero.manager.imports.models.statements.interfaces import AnyImportStatement
from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.collection import ImportStatementContainer


def parse_import_lines_return_import_models(import_lines: List[str]) -> ImportStatementContainer:
    # Convert multiline imports into single line imports
    import_statements = combine_imports_lines_into_import_statements(import_lines)

    return ImportStatementContainer(
        [_parse_import_statement_str_return_import_model(import_statement) for import_statement in import_statements]
    )

def _parse_import_statement_str_return_import_model(import_str: str) -> AnyImportStatement:
    import_str, renames = pre_process_import_statement_get_renames(import_str)

    if is_module_import(import_str):
        return ModuleImportStatement.from_str(import_str, renames=renames)
    elif is_obj_import(import_str):
        return ObjectImportStatement.from_str(import_str, renames=renames)
    else:
        raise ValueError(f'could not parse import statement {import_str} into module or object import')
