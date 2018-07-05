from typing import List

from dero.manager.imports.logic.parse.combine import combine_imports_lines_into_import_statements
from dero.manager.imports.logic.parse.clean import pre_process_import_statement_get_renames
from dero.manager.imports.logic.parse.classify import is_module_import, is_obj_import
from dero.manager.imports.logic.parse.extract import extract_line_without_comment_and_comment_from_line
from dero.manager.imports.models.statements.interfaces import AnyImportStatement
from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.imports.models.statements.comment import Comment


def parse_import_lines_return_import_models(import_lines: List[str]) -> ImportStatementContainer:
    # TODO: handle comments which are inside parentheses, for multiline import. Will need to handle before combining.
    # Convert multiline imports into single line imports
    import_statements = combine_imports_lines_into_import_statements(import_lines)

    return ImportStatementContainer(
        [_parse_import_statement_str_return_import_model(import_statement) for import_statement in import_statements]
    )

def _parse_import_statement_str_return_import_model(import_str: str) -> AnyImportStatement:
    import_str, comment_str = extract_line_without_comment_and_comment_from_line(import_str)

    if comment_str.strip() is not '':
        comment = Comment(comment_str)
    else:
        comment = None

    if import_str.strip() is '':
        return comment

    import_str, renames = pre_process_import_statement_get_renames(import_str)

    if is_module_import(import_str):
        return ModuleImportStatement.from_str(import_str, renames=renames, comment=comment)
    elif is_obj_import(import_str):
        return ObjectImportStatement.from_str(import_str, renames=renames, comment=comment)
    else:
        raise ValueError(f'could not parse import statement {import_str} into module or object import')
