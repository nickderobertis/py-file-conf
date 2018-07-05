from typing import List

from dero.mixins.repr import ReprMixin

from dero.manager.imports.models.statements.importbase import ImportStatement
from dero.manager.imports.models.statements.rename import RenameStatementCollection
from dero.manager.imports.logic.parse.extract import _extract_modules_from_module_import
from dero.manager.imports.models.statements.comment import Comment

class ModuleImportStatement(ImportStatement, ReprMixin):
    rename_attr = 'modules'
    repr_cols = ['modules', 'renames', 'comment']
    equal_attrs = ['modules', 'renames', 'comment']

    def __init__(self, modules: List[str], renames: RenameStatementCollection = None, comment: Comment=None):
        self.modules = modules
        self.renames = renames
        self.comment = comment

    def __str__(self):
        modules = self._renamed
        modules_str = ', '.join(modules)
        return f'import {modules_str} {self.comment if self.comment is not None else ""}'

    @classmethod
    def from_str(cls, import_str: str, renames: RenameStatementCollection = None, comment: Comment=None):
        modules = _extract_modules_from_module_import(import_str)

        return cls(modules=modules, renames=renames, comment=comment)