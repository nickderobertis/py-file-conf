from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.config.models.config import FunctionConfig

from dero.manager.basemodels.file import ConfigFileBase


class FunctionConfigFile(ConfigFileBase):
    """
    Represents config file on filesystem. Handles low-level functions for writing and reading config file
    """

    def load(self) -> 'FunctionConfig':
        from dero.manager.config.models.config import FunctionConfig

        config_dict = self._load_into_config_dict()

        return FunctionConfig(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)



