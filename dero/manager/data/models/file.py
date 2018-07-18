
from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement

class DataConfigFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = [ObjectImportStatement.from_str('from dero.manager import Selector', preferred_position='begin')]

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = [
        AssignmentStatement.from_str('s = Selector()', preferred_position='begin'),
        AssignmentStatement.from_str('loader_func_kwargs = dict(\n    \n)', preferred_position='end')
    ]

    # class to use for interfacing with file
    # no need to override default
    # interface_class = ConfigFileInterface