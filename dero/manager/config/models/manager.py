from typing import List, Union

from dero.manager.config.models.interfaces import ConfigSectionOrConfig
from dero.manager.config.models.section import ConfigSection
from dero.manager.sectionpath.sectionpath import SectionPath

class ConfigManager:

    def __init__(self, basepath: str, main_section: ConfigSection=None):
        self.section = main_section
        self.basepath = basepath

    def load(self):
        self.section = ConfigSection.from_files(self.basepath)

    def update(self, d: dict, section_path_str: str=None, **kwargs) -> None:
        config_obj = self.get(section_path_str)
        config_obj.update(d, **kwargs)

    def get(self, section_path_str: str=None) -> ConfigSectionOrConfig:
        if section_path_str is None:
            section_path_str = self.section.name

        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final config or section
        obj = self
        for section in section_path:
            obj = getattr(obj, section)

        return obj




