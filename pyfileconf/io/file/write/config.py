from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.basemodels.config import ConfigBase

from pyfileconf.io.file.write.base import FileStr

from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.assignments.models.container import AssignmentStatementContainer

class ConfigFileStr(FileStr):

    def __init__(self, config: 'ConfigBase', existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer, existing_body: List[str]):
        super().__init__(
            config,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns,
            existing_body=existing_body
        )