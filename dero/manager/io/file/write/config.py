from dero.manager.io.file.write.base import FileStr
from dero.manager.basemodels.config import ConfigBase
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer

class ConfigFileStr(FileStr):

    def __init__(self, config: ConfigBase, existing_imports: ImportStatementContainer,
                 existing_assigns: AssignmentStatementContainer):
        super().__init__(
            config,
            existing_imports=existing_imports,
            existing_assigns=existing_assigns
        )