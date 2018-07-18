
from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement

class FunctionConfigFile(ConfigFileBase):
    """
    Represents config file on filesystem. Handles low-level functions for writing and reading config file
    """

    # lines to always import. pass import objects
    always_imports = [
        ObjectImportStatement.from_str('from dero.manager import Selector, MergeOptions', preferred_position='begin')
    ]

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = [AssignmentStatement.from_str('s = Selector()', preferred_position='begin')]

    # class to use for interfacing with file
    # no need to override default
    # interface_class = ConfigFileInterface

