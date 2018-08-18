from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.data.models.config import DataConfig

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.manager.data.models.source import DataSource
from dero.manager.io.file.interfaces.activeconfig import ActiveConfigFileInterface
from dero.manager.data.models.astitems import ast_dict_constructor_with_kwargs_from_dict

class DataConfigFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = [ObjectImportStatement.from_str('from dero.manager import Selector', preferred_position='begin')]

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = [
        AssignmentStatement.from_str('s = Selector()', preferred_position='begin'),
        AssignmentStatement.from_str('loader_func_kwargs = dict(\n    \n)', preferred_position='end')
    ]

    def load(self, config_class: type = None) -> 'DataConfig':
        # Override base class method to pull a single dict, and not pass annotations
        from dero.manager.data.models.config import DataConfig

        # Data configs are a hybrid of the ast/static config and the active config
        self.active_interface = ActiveConfigFileInterface(self.interface.filepath)

        config_dict, annotation_dict = self.interface.load()
        user_defined_dict = self.active_interface.load()

        if config_class is None:
            config_class = DataConfig

        return config_class(
            d=config_dict,
            annotations=annotation_dict,
            active_config_dict=user_defined_dict,
            imports=self.interface.imports,
            _file=self,
            name=self.name
        )