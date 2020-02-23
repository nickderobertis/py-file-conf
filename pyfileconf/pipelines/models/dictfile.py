from typing import List

from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.io.file.interfaces.pipeline import PipelineDictInterface

class PipelineDictFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports: List[AssignmentStatement] = []

    # assignment lines to always include at beginning. pass assign objects
    # no need to override default
    # always_assigns = []

    # class to use for interfacing with file
    # no need to override default
    interface_class = PipelineDictInterface

    def load(self) -> dict:  # type: ignore
        return self.interface.load()