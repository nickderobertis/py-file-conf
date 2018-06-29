from typing import List
import os

from dero.manager.basemodels.container import Container
from dero.manager.config.models.config import Config


class ConfigSection(Container):

    def __init__(self, configs: List[Config, 'ConfigSection'], section_config: Config=None):
        self.config = section_config
        self.items = configs

    def update(self, d: dict, **kwargs):
        self.config.update(d)
        self.config.update(kwargs)

    @classmethod
    def from_files(cls, basepath: str):
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

        return cls(configs, section_config=section_config)