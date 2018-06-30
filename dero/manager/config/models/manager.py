from typing import List, Union

from dero.manager.logic.get import _get_from_nested_obj_by_section_path
from dero.manager.config.models.interfaces import ConfigSectionOrConfig
from dero.manager.config.models.section import ConfigSection, Config
from dero.manager.sectionpath.sectionpath import SectionPath

class ConfigManager:

    def __init__(self, basepath: str, main_section: ConfigSection=None):
        self.section = main_section
        self.basepath = basepath

    def load(self):
        self.section = ConfigSection.from_files(self.basepath)

    def update(self, d: dict, section_path_str: str=None, **kwargs) -> None:
        config_obj = self._get_func_or_section_config(section_path_str)
        config_obj.update(d, **kwargs)

    def get(self, section_path_str: str=None) -> Config:
        """
        Handles config inheritance to get the active config for a section or function

        Args:
            section_path_str:

        Returns:

        """
        config = self._get_func_or_section_config(section_path_str)

        # Get configs, in order of highest level to lowest level. Will go from project to highest section,
        # down to lowest section.
        section_path = SectionPath(section_path_str)
        full_section = ''
        section_configs = []
        for section in section_path:
            full_section += section # rebuilding full section path str
            section_configs.append(
                self._get_func_or_section_config(full_section)
            )
            full_section += '.'

        # Override configs. Default config is base config, then gets updated by project, then high
        # level sections to low level sections
        [config.update(section_config) for section_config in section_configs]

        return config

    def _get_func_or_section_config(self, section_path_str: str=None) -> ConfigSectionOrConfig:
        """
        This get method is used to get only the config for the section path, without handling
        multiple levels of config and overriding. To get the active config for a function,
        use regular get method.

        Args:
            section_path_str:

        Returns:

        """
        if section_path_str is None:
            section_path_str = self.section.name

        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final config or section
        return _get_from_nested_obj_by_section_path(self, section_path)




