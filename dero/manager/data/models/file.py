from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.data.models.config import DataConfig

from dero.manager.basemodels.file import ConfigFileBase

class DataConfigFile(ConfigFileBase):

    def load(self) -> 'DataConfig':
        from dero.manager.data.models.config import DataConfig

        config_dict = self._load_into_config_dict()

        return DataConfig(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)