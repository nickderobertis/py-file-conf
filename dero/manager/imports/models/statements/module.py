from typing import List, Dict
import ast
import importlib
from types import ModuleType

from dero.mixins.repr import ReprMixin

from dero.manager.imports.models.statements.importbase import ImportStatement
from dero.manager.imports.models.statements.rename import RenameStatementCollection
from dero.manager.imports.logic.parse.extract import _extract_modules_from_module_import
from dero.manager.imports.models.statements.comment import Comment
from dero.manager.imports.logic.load.ext_importlib import get_filepath_from_module_str


class ModuleImportStatement(ImportStatement, ReprMixin):
    rename_attr = 'modules'
    repr_cols = ['modules', 'renames', 'comment']
    equal_attrs = ['modules', 'renames', 'comment']

    def __init__(self, modules: List[str], renames: RenameStatementCollection = None, comment: Comment=None):

        if renames is None:
            renames = RenameStatementCollection([])

        self.modules = modules
        self.renames = renames
        self.comment = comment

    def __str__(self):
        modules = self._renamed
        modules_str = ', '.join(modules)
        import_str = f'import {modules_str}'
        if self.comment is not None:
            import_str += f' {self.comment}'

        return import_str

    @classmethod
    def from_str(cls, import_str: str, renames: RenameStatementCollection = None, comment: Comment=None):
        modules = _extract_modules_from_module_import(import_str)

        return cls(modules=modules, renames=renames, comment=comment)

    @classmethod
    def from_ast_import(cls, ast_import: ast.Import):

        # Create RenameStatementCollection
        renames = RenameStatementCollection.from_ast_import(ast_import)

        # Get module original names
        modules = [alias.name for alias in ast_import.names]

        return cls(
            modules,
            renames
        )

    def get_module_filepaths(self, import_section_path_str: str=None) -> Dict[str, str]:
        return {module: get_filepath_from_module_str(module, import_section_path_str) for module in self.modules}

    def execute(self, import_section_path_str: str=None) -> List[ModuleType]:
        return [importlib.import_module(mod_str, import_section_path_str) for mod_str in self.modules]
