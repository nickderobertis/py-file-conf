from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.config.models.config import ActiveFunctionConfig

from pyfileconf.pipelines.models.file import FunctionConfigFile
from pyfileconf.io.file.interfaces.activeconfig import ActiveConfigFileInterface

class ActiveFunctionConfigFile(FunctionConfigFile):
    # class to use for interfacing with file
    # no need to override default
    interface_class = ActiveConfigFileInterface


    def load(self, config_class: type = None) -> 'ActiveFunctionConfig':
        # Override base class method to pull a single dict, and not pass annotations
        from pyfileconf.config.models.config import ActiveFunctionConfig
        user_defined_dict = self.interface.load()

        if config_class is None:
            config_class = ActiveFunctionConfig

        return config_class(
            d=user_defined_dict,
            imports=self.interface.imports,
            _file=self,
            name=self.name
        )