from typing import Union
import ast

from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.comment import Comment

AnyAstImport = Union[ast.Import, ast.ImportFrom]
AnyImportStatement = Union[ModuleImportStatement, ObjectImportStatement]
AnyImportStatementOrComment = Union[AnyImportStatement, Comment]
ImportOrNone = Union[AnyImportStatement, None]