from typing import Union
import ast

from pyfileconf.imports.models.statements.module import ModuleImportStatement
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.imports.models.statements.comment import Comment

AnyAstImport = Union[ast.Import, ast.ImportFrom]
AnyImportStatement = Union[ModuleImportStatement, ObjectImportStatement]
AnyImportStatementOrComment = Union[AnyImportStatement, Comment]
ImportOrNone = Union[AnyImportStatement, None]