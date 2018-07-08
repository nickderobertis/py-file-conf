from dero.manager.imports.logic.parse.patterns import re_patterns

def is_obj_import(import_str: str) -> bool:
    pattern = re_patterns['obj import']
    match = pattern.fullmatch(import_str)

    if match is None:
        return False

    return True

def is_module_import(import_str: str) -> bool:
    pattern = re_patterns['module import']
    match = pattern.fullmatch(import_str)

    if match is None:
        return False

    return True