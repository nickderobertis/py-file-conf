from typing import List, Union, Any

from dero.mixins.repr import ReprMixin
from dero.manager.logic.get import _get_from_nested_obj_by_section_path
from dero.manager.config.models.interfaces import ConfigSectionOrConfig
from dero.manager.config.models.section import ConfigSection, FunctionConfig
from dero.manager.sectionpath.sectionpath import SectionPath

class ConfigManager(ReprMixin):
    repr_cols = ['basepath', 'section']

    def __init__(self, basepath: str, main_section: ConfigSection=None):
        self.section = main_section
        self.basepath = basepath
        self.local_config = FunctionConfig()

    def __getattr__(self, item):
        return getattr(self.section, item)

    def __dir__(self):
        exposed_methods = [
            'load',
            'get',
            'update'
        ]
        exposed_attrs = [
            'basepath',
        ]
        return exposed_methods + exposed_attrs + list(self.section.config_map.keys())

    def load(self):
        self.section = ConfigSection.from_files(self.basepath)

    def update(self, d: dict=None, section_path_str: str=None, **kwargs) -> None:
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        config_obj.update(d, **kwargs)

    def pop(self, key: str, section_path_str: str=None) -> Any:
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        return config_obj.pop(key)

    def get(self, section_path_str: str=None) -> FunctionConfig:
        """
        Handles config inheritance to get the active config for a section or function

        Args:
            section_path_str:

        Returns:

        """
        config = self._get_func_or_section_config(section_path_str)

        # First override for function defaults is global project config
        section_configs = [self.section.config]

        # Get configs, in order of highest level to lowest level. Will go from project to highest section,
        # down to lowest section.
        section_path = SectionPath(section_path_str)
        full_section = ''
        for section in section_path[:-1]: # skip the last section or function for special handling at end
            full_section += section # rebuilding full section path str
            section_configs.append(
                self._get_func_or_section_config(full_section)
            )
            full_section += '.'

        # Last item of section_path may be another section, or the function/Pipeline itself. If it's a section,
        # must add config for override, but if is function, it is already the base config so should not update.
        full_section += section_path[-1]
        if not self._is_function_or_pipeline_path(full_section):
            # if is a section, not function/pipeline
            section_configs.append(self._get_func_or_section_config(full_section))

        # Override configs. Default config is base config, then gets updated by project, then high
        # level sections to low level sections
        [config.update(section_config) for section_config in section_configs]

        # Last, override with local config
        config.update(self.local_config)

        return config

    def _get_func_or_section_config(self, section_path_str: str=None) -> FunctionConfig:
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
        config_or_section: ConfigSectionOrConfig = _get_from_nested_obj_by_section_path(self, section_path)
        return _get_config_from_config_or_section(config_or_section)


    def _is_function_or_pipeline_path(self, section_path_str: str) -> bool:
        section_path = SectionPath(section_path_str)
        # Goes into nested sections, until it pulls the final config or section
        config_or_section: ConfigSectionOrConfig = _get_from_nested_obj_by_section_path(self, section_path)
        if isinstance(config_or_section, ConfigSection):
            # must be section, not individual pipeline or function
            return False
        elif isinstance(config_or_section, FunctionConfig):
            # must be individual function as Config is returned
            return True
        else:
            raise ValueError(f'expected Config or ConfigSection, got {config_or_section} of type {config_or_section}')

    def _get_project_config_or_local_config_by_section_path(self, section_path_str: str) -> FunctionConfig:
        if section_path_str is not None:
            config_obj = self._get_func_or_section_config(section_path_str)
        else:
            # If no section passed, update local config
            config_obj = self.local_config

        return config_obj


def _get_config_from_config_or_section(config_or_section: ConfigSectionOrConfig) -> FunctionConfig:
    # Pull Config from ConfigSection
    if isinstance(config_or_section, ConfigSection):
        return config_or_section.config
    elif isinstance(config_or_section, FunctionConfig):
        return config_or_section
    else:
        raise ValueError(f'expected Config or ConfigSection, got {config_or_section} of type {config_or_section}')
