from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.data.models.config import DataConfig

from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.io.file.interfaces.activeconfig import ActiveConfigFileInterface


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
        from pyfileconf.data.models.config import DataConfig

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