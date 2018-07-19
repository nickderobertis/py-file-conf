from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.io.file.interfaces.pipeline import PipelineDictInterface

class PipelineDictFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = [
        ObjectImportStatement.from_str('from dero.manager import DataPipeline', preferred_position='begin')
    ]

    # assignment lines to always include at beginning. pass assign objects
    # no need to override default
    # always_assigns = []

    # class to use for interfacing with file
    # no need to override default
    interface_class = PipelineDictInterface

    def load(self) -> dict:
        return self.interface.load()