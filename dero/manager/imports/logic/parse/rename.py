from typing import List

from dero.manager.imports.logic.parse.patterns import re_patterns
from dero.manager.imports.models.statements.rename import RenameStatementCollection

def _replace_renames(import_str: str, extracted_renames: RenameStatementCollection) -> str:
    for rename in extracted_renames:
        orig_str = rename._orig_str
        import_str = import_str.replace(orig_str, rename.item)

    return import_str

def _extract_renames(import_str: str) -> List[str]:
    pattern = re_patterns['rename']
    return pattern.findall(import_str)