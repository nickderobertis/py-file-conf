from typing import List, Union
import os
import warnings

from mixins.repr import ReprMixin
from pyfileconf.basemodels.container import Container
from pyfileconf.config.models.config import ActiveFunctionConfig
from pyfileconf.exceptions.config import ConfigManagerNotLoadedException
from pyfileconf.sectionpath.sectionpath import _strip_py


class ConfigSection(Container, ReprMixin):
    repr_cols = ['name', 'config', 'items']

    def __init__(self, configs: List[Union[ActiveFunctionConfig, 'ConfigSection']],
                 section_config: ActiveFunctionConfig=None, name: str=None):
        self.config = section_config
        self.items = configs
        self.name = name

    def __getattr__(self, item):

        # Handle if trying to get this section's config
        if self.config is not None and item == self.config.name:
            return self.config

        return self.config_map[item]

    def __dir__(self):
        return self.config_map.keys()

    @property  # type: ignore
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items
        self._set_config_map() # recreate config map on setting items

    @property
    def config_map(self):
        return self._config_map

    def _set_config_map(self):
        config_map = {}
        for config in self:
            if config.name is None:
                warnings.warn(f"Couldn't determine name of config {config}. Can't add to mapping.")
                continue
            config_map[config.name] = config
        self._config_map = config_map

    def update(self, d: dict=None, **kwargs):
        if self.config is None:
            raise ConfigManagerNotLoadedException('no config in ConfigSection')
        if d is not None:
            self.config.update(d)
        self.config.update(kwargs)

    @classmethod
    def from_files(cls, basepath: str):

        # Get section name by name of folder
        name = os.path.basename(os.path.abspath(basepath))

        # Config folder doesn't exist, return empty config
        if not os.path.exists(basepath):
            return cls([], name=name)

        config_file_list = [file for file in next(os.walk(basepath))[2] if file.endswith('.py')]

        # Ignore folders starting with . or _
        config_section_list = [
            folder for folder in next(os.walk(basepath))[1] if not any(
                [folder.startswith(item) for item in ('_','.')]
            )
        ]

        # Special handling for section config
        try:
            config_file_list.remove('section.py')
            section_config = ActiveFunctionConfig.from_file(os.path.join(basepath, 'section.py'), name=name)
        except ValueError:
            # Didn't find section config
            section_config = None

        configs = [
            ActiveFunctionConfig.from_file(
                os.path.join(basepath, file),
                name=_strip_py(file)
            ) for file in config_file_list
        ]
        # Recursively calling section creation to create individual config files
        config_sections = [ConfigSection.from_files(os.path.join(basepath, folder)) for folder in config_section_list]

        configs += config_sections

        return cls(configs, section_config=section_config, name=name)

