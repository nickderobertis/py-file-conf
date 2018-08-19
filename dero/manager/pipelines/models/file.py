from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.basemodels.config import ConfigBase

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.io.file.write.asttosource import ast_node_to_source

class FunctionConfigFile(ConfigFileBase):
    """
    Represents config file on filesystem. Handles low-level functions for writing and reading config file
    """

    # lines to always import. pass import objects
    always_imports = [
        ObjectImportStatement.from_str('from dero.manager import Selector, MergeOptions', preferred_position='begin')
    ]

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = [
        AssignmentStatement.from_str('s = Selector()', preferred_position='begin'),
    ]

    # always assign dict, where assigns will get added if item name matches dict key
    always_assign_with_names_dict = {
        'DataPipeline': [
            AssignmentStatement.from_str('cleanup_kwargs = dict(\n    \n)', preferred_position='end')
        ]
    }

    # class to use for interfacing with file
    # no need to override default
    # interface_class = ConfigFileInterface

    def save(self, config: 'ConfigBase'):
        # If empty cleanup kwargs on DataPipeline, then delete so can be replaced with dict() constructor
        # from always assigns
        if _should_replace_cleanup_kwargs(self, config):
            config.pop('cleanup_kwargs')

        super().save(config)


def _should_replace_cleanup_kwargs(config_file: FunctionConfigFile, config: 'ConfigBase') -> bool:
    return all([
        config_file.name == 'DataPipeline',
        'cleanup_kwargs' in config
    ]) and ast_node_to_source(config['cleanup_kwargs']) == 'None\n'