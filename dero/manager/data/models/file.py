from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.data.models.config import DataConfig

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.data.models.source import DataSource

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

    def save(self, config: 'DataConfig'):

        # When loading the config from file, loader_func_kwargs were spread into the individual kwargs.
        # Now need to combine back into loader_func_kwargs, as to not add those to the file
        loader_func_kwargs = {key: value for key, value in config.items() if key not in DataSource._scaffold_items}
        [config.pop(key) for key in loader_func_kwargs]  # remove individual kwargs
        # TODO: use ast to create dict() constructor
        config.update({'loader_func_kwargs': loader_func_kwargs})

        super().save(config)