from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.io.file.interfaces.datadict import DataDictInterface

class DataDictFile(ConfigFileBase):
    # lines to always import. pass import objects
    # no need to override default
    # always_imports = []

    # assignment lines to always include at beginning. pass assign objects
    # no need to override default
    # always_assigns = []

    # class to use for interfacing with file
    # no need to override default
    interface_class = DataDictInterface

    def load(self) -> dict:
        return self.interface.load()