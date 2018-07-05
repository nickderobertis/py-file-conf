from typing import Tuple

from dero.manager.imports.logic.parse.rename import (
    _extract_renames,
    _replace_renames,
    RenameStatementCollection
)


def pre_process_import_statement_get_renames(import_str: str) -> Tuple[str, RenameStatementCollection]:
    import_str = _clean_import_statement(import_str)
    rename_strs = _extract_renames(import_str)
    rename_statements = RenameStatementCollection.from_str_list(rename_strs)
    import_str = _replace_renames(import_str, rename_statements)

    return import_str, rename_statements

def _clean_import_statement(import_str: str) -> str:
    remove_chars = [
        '(',
        ')',
        '\\',
    ]
    for char in remove_chars:
        import_str = import_str.replace(char, '')

    return import_str