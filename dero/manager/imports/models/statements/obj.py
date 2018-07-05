from typing import List

from dero.mixins.repr import ReprMixin

from dero.manager.imports.models.statements.importbase import ImportStatement
from dero.manager.imports.models.statements.rename import RenameStatementCollection
from dero.manager.imports.logic.parse.extract import _extract_module_and_objs_from_obj_import

class ObjectImportStatement(ImportStatement, ReprMixin):
    rename_attr = 'objs'
    repr_cols = ['module', 'objs', 'renames']

    def __init__(self, objs: List[str], module: str, renames: RenameStatementCollection = None):
        self.objs = objs
        self.module = module
        self.renames = renames

    def __str__(self):
        objs = self._renamed
        objs_str = ', '.join(objs)
        return f'from {self.module} import {objs_str}'

    @classmethod
    def from_str(cls, import_str: str, renames: RenameStatementCollection = None):
        module, objs = _extract_module_and_objs_from_obj_import(import_str)

        return cls(objs=objs, module=module, renames=renames)