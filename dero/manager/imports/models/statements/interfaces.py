from typing import Union

from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.comment import Comment

AnyImportStatement = Union[ModuleImportStatement, ObjectImportStatement]
AnyImportStatementOrComment = Union[AnyImportStatement, Comment]