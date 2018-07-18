from typing import List
import ast
import importlib

from dero.mixins.repr import ReprMixin

from dero.manager.imports.models.statements.importbase import ImportStatement
from dero.manager.imports.models.statements.rename import RenameStatementCollection
from dero.manager.imports.logic.parse.extract import _extract_module_and_objs_from_obj_import
from dero.manager.imports.models.statements.comment import Comment
from dero.manager.imports.logic.load.ext_importlib import get_filepath_from_module_str


class ObjectImportStatement(ImportStatement, ReprMixin):
    rename_attr = 'objs'
    repr_cols = ['module', 'objs', 'renames', 'comment']
    equal_attrs = ['module', 'objs', 'renames', 'comment']

    def __init__(self, objs: List[str], module: str, renames: RenameStatementCollection = None, comment: Comment=None,
                 preferred_position: str = None):

        if renames is None:
            renames = RenameStatementCollection([])

        self.objs = objs
        self.module = module
        self.renames = renames
        self.comment = comment
        self.preferred_position = preferred_position

    def __str__(self):
        objs = self._renamed
        objs_str = ', '.join(objs)
        import_str = f'from {self.module} import {objs_str}'
        if self.comment is not None:
            import_str += f' {self.comment}'

        return import_str

    @classmethod
    def from_str(cls, import_str: str, renames: RenameStatementCollection = None, comment: Comment=None,
                 preferred_position: str = None):
        module, objs = _extract_module_and_objs_from_obj_import(import_str)

        return cls(objs=objs, module=module, renames=renames, comment=comment, preferred_position=preferred_position)

    @classmethod
    def from_ast_import_from(cls, ast_import: ast.ImportFrom, preferred_position: str = None):

        # Create RenameStatementCollection
        renames = RenameStatementCollection.from_ast_import(ast_import)

        # Collect object names
        objs = [alias.name for alias in ast_import.names]

        return cls(
            objs,
            ast_import.module,
            renames,
            preferred_position=preferred_position
        )

    def get_module_filepath(self, import_section_path_str: str=None) -> str:
        return get_filepath_from_module_str(self.module, import_section_path_str)

    def execute(self, import_section_path_str: str=None) -> list:
        module = importlib.import_module(self.module, import_section_path_str)
        return [getattr(module, obj_name) for obj_name in self.objs]