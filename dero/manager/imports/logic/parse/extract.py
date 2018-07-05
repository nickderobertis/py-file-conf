from typing import Tuple, List

from dero.manager.imports.logic.parse.patterns import re_patterns

def _extract_module_and_objs_from_obj_import(import_str: str) -> Tuple[str, List[str]]:
    pattern = re_patterns['obj import']
    match = pattern.fullmatch(import_str)

    if match is None:
        raise ValueError(f'could not parse import str {import_str} as object import')

    module, objs_str, _ = match.groups()
    return module, [obj.strip() for obj in objs_str.split(',')]

def _extract_modules_from_module_import(import_str: str) -> List[str]:
    pattern = re_patterns['module import']
    match = pattern.fullmatch(import_str)

    if match is None:
        raise ValueError(f'could not parse import str {import_str} as module import')

    module_str, _ = match.groups()
    return [module.strip() for module in module_str.split(',')]