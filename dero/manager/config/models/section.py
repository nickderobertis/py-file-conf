from typing import List, Union
import os
import warnings

from dero.manager.basemodels.container import Container
from dero.manager.config.models.config import Config
from dero.manager.pipelines.models.interfaces import PipelineOrFunction


class ConfigSection(Container):

    def __init__(self, configs: List[Union[Config, 'ConfigSection']], section_config: Config=None, name: str=None):
        self.config = section_config
        self.items = configs
        self.name = name

    def __getattr__(self, item):
        return self.config_map[item]

    def __dir__(self):
        return self.config_map.keys()

    @property
    def config_map(self):
        if hasattr(self, '_config_map'):
            return self._config_map

        self._set_config_map()
        return self._config_map

    def _set_config_map(self):
        config_map = {}
        for config in self:
            if config.name is None:
                warnings.warn(f"Couldn't determine name of config {config}. Can't add to mapping.")
                continue
            config_map[config.name] = config
        self._config_map = config_map

    def update(self, d: dict, **kwargs):
        self.config.update(d)
        self.config.update(kwargs)

    @classmethod
    def from_files(cls, basepath: str):

        # Get section name by name of folder
        name = os.path.basename(os.path.abspath(basepath))

        config_file_list = [file for file in next(os.walk(basepath))[2] if file.endswith('.py')]

        # Ignore folders starting with . or _
        config_section_list = [
            folder for folder in next(os.walk(basepath))[1] if not any(
                [folder.startswith(item) for item in ('_','.')]
            )
        ]

        # Special handling for section config
        config_file_list.remove('section.py')
        section_config = Config.from_file(os.path.join(basepath, 'section.py'))

        configs = [Config.from_file(os.path.join(basepath, file)) for file in config_file_list]
        # Recursively calling section creation to create individual config files
        config_sections = [ConfigSection.from_files(os.path.join(basepath, folder)) for folder in config_section_list]

        configs += config_sections

        return cls(configs, section_config=section_config, name=name)

