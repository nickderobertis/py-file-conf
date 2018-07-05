from typing import Union

from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.obj import ObjectImportStatement

AnyImportStatement = Union[ModuleImportStatement, ObjectImportStatement]