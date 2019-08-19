from typing import List, Dict
import ast
import importlib
from types import ModuleType

from mixins.repr import ReprMixin

from dero.manager.imports.models.statements.importbase import ImportStatement
from dero.manager.imports.models.statements.rename import RenameStatementCollection
from dero.manager.imports.models.statements.comment import Comment
from dero.manager.imports.logic.load.ext_importlib import get_filepath_from_module_str


class ModuleImportStatement(ImportStatement, ReprMixin):
    rename_attr = 'modules'
    repr_cols = ['modules', 'renames', 'comment']
    equal_attrs = ['modules', 'renames', 'comment']

    def __init__(self, modules: List[str], renames: RenameStatementCollection = None, comment: Comment=None,
                 preferred_position: str = None):

        if renames is None:
            renames = RenameStatementCollection([])

        self.modules = modules
        self.renames = renames
        self.comment = comment
        self.preferred_position = preferred_position  # sets self.prefer_beginning as bool

    def __str__(self):
        modules = self._renamed
        modules_str = ', '.join(modules)
        import_str = f'import {modules_str}'
        if self.comment is not None:
            import_str += f' {self.comment}'

        return import_str

    @classmethod
    def from_str(cls, import_str: str, renames: RenameStatementCollection = None, comment: Comment=None,
                 preferred_position: str = None):
        from dero.manager.io.file.load.parsers.imp import extract_module_import_from_ast
        ast_module = ast.parse(import_str)
        cls_obj = extract_module_import_from_ast(ast_module)
        cls_obj.comment = comment
        cls_obj.preferred_position = preferred_position

        return cls_obj

    @classmethod
    def from_ast_import(cls, ast_import: ast.Import, preferred_position: str = None):

        # Create RenameStatementCollection
        renames = RenameStatementCollection.from_ast_import(ast_import)

        # Get module original names
        modules = [alias.name for alias in ast_import.names]

        return cls(
            modules,
            renames,
            preferred_position=preferred_position
        )

    def get_module_filepaths(self, import_section_path_str: str=None) -> Dict[str, str]:
        return {module: get_filepath_from_module_str(module, import_section_path_str) for module in self.modules}

    def execute(self, import_section_path_str: str=None) -> List[ModuleType]:
        return [importlib.import_module(mod_str, import_section_path_str) for mod_str in self.modules]

    @property
    def module(self):
        if len(self.modules) > 1:
            raise ValueError('cannot get one module, import has multiple modules')

        return self.modules[0]
