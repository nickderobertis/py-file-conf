from typing import List

from dero.manager.basemodels.config import ConfigBase
from dero.manager.data.models.source import DataSource
from dero.manager.data.models.file import DataConfigFile

class DataConfig(ConfigBase):
    config_file_class = DataConfigFile


    @classmethod
    def from_source(cls, data_source: DataSource, name: str=None, loaded_modules: List[str]=None):
        # Initialize a blank config dictionary
        config_dict = {attr: None for attr in DataSource._scaffold_items}

        # Fill blank config dict
        for config_attr in config_dict:
            if hasattr(data_source, config_attr):
                config_dict[config_attr] = getattr(data_source, config_attr)

        # Handle loader func kwargs. They are saved as a dict in data source, but when passing to
        # init, they are spread. Therefore save as their own items in config dict
        for config_attr, config_value in data_source.loader_func_kwargs.items():
            config_dict[config_attr] = config_value

        return cls(config_dict, name=name, _loaded_modules=loaded_modules)

