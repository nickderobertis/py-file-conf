import os
from typing import Union, Any, Optional

from mixins.repr import ReprMixin

from pyfileconf.config.models.file import ActiveFunctionConfigFile
from pyfileconf.exceptions.config import ConfigManagerNotLoadedException
from pyfileconf.logic.get import _get_from_nested_obj_by_section_path
from pyfileconf.logic.set import _set_in_nested_obj_by_section_path
from pyfileconf.config.models.interfaces import ConfigSectionOrConfig
from pyfileconf.config.models.section import ConfigSection, ActiveFunctionConfig
from pyfileconf.pipelines.models.file import FunctionConfigFile
from pyfileconf.sectionpath.sectionpath import SectionPath

class ConfigManager(ReprMixin):
    repr_cols = ['basepath', 'section']

    def __init__(self, basepath: str, main_section: ConfigSection=None):
        self.section = main_section
        self.basepath = basepath
        self.local_config = ActiveFunctionConfig()

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
        if config_obj is None:
            raise ConfigManagerNotLoadedException('no config to update')
        config_obj.update(d, **kwargs)

    def refresh(self, section_path_str: str):
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        if config_obj is None:
            raise ConfigManagerNotLoadedException('no config to refresh')
        config_obj.refresh()

    def reset(self, section_path_str: str=None, allow_create: bool = False) -> None:
        """
        Resets a function or section config to default. If no section_path_str is passed, resets local config.

        To reset all configs, use .load() instead.

        Args:
            section_path_str:

        Returns:

        """
        default = self._get_default_func_or_section_config(section_path_str, create=allow_create)
        self.set(section_path_str, default, allow_create=allow_create)

    def pop(self, key: str, section_path_str: str=None) -> Any:
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        if config_obj is None:
            raise ConfigManagerNotLoadedException('no config to pop')
        return config_obj.pop(key)

    def get(self, section_path_str: str) -> Optional[ActiveFunctionConfig]:
        """
        Handles config inheritance to get the active config for a section or function

        Args:
            section_path_str:

        Returns:

        """
        config = self._get_func_or_section_configs(section_path_str)

        if self.section is None:
            raise ConfigManagerNotLoadedException('call .load() on ConfigManager before .get()')

        # First override for function defaults is global project config
        section_configs = [self.section.config]

        # Get configs, in order of highest level to lowest level. Will go from project to highest section,
        # down to lowest section.
        section_path = SectionPath(section_path_str)
        full_section = ''
        for section in section_path[:-1]: # skip the last section or function for special handling at end
            full_section += section # rebuilding full section path str
            section_configs.append(
                self._get_func_or_section_configs(full_section)
            )
            full_section += '.'

        # Last item of section_path may be another section, or the function/Pipeline itself. If it's a section,
        # must add config for override, but if is function, it is already the base config so should not update.
        full_section += section_path[-1]
        if not self._is_function_or_pipeline_path(full_section):
            # if is a section, not function/pipeline
            section_configs.append(self._get_func_or_section_configs(full_section))

        if config:
            # Override configs. Default config is base config, then gets updated by project, then high
            # level sections to low level sections
            [config.update(section_config) for section_config in section_configs]

            # Last, override with local config
            config.update(self.local_config)

        return config

    def set(self, section_path_str: str=None, value=None, allow_create: bool = True):
        """
        In contrast to update, completely replaces the config object.

        Args:
            section_path_str:
            value:

        Returns:

        """

        if value == None: # empty config
            value = ActiveFunctionConfig()

        if section_path_str is None:
            # updating local config
            self.local_config = value
            return

        self._set_func_or_section_config(section_path_str, value=value, allow_create=allow_create)


    def _get_func_or_section_configs(self, section_path_str: str) -> Optional[ActiveFunctionConfig]:
        """
        This get method is used to get only the config for the section path, without handling
        multiple levels of config and overriding. To get the active config for a function,
        use regular get method.

        Args:
            section_path_str:

        Returns:

        """
        if self.section is None:
            raise ConfigManagerNotLoadedException('call .load() on ConfigManager before .get()')

        if section_path_str is None:
            section_path_str = self.section.name

        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final config or section
        config_or_section: ConfigSectionOrConfig = _get_from_nested_obj_by_section_path(self, section_path)
        conf = _get_config_from_config_or_section(config_or_section)

        # Now update stored config as loading may have happened during _get_config_from_config_or_section
        # Want to keep the active config once it is loaded
        # But if it is a section, then don't want to overwrite with config
        if not isinstance(config_or_section, ConfigSection):
            _set_in_nested_obj_by_section_path(self, section_path, conf)

        return conf

    def _set_func_or_section_config(self, section_path_str: str, value=None, allow_create: bool = True) -> None:
        if self.section is None:
            raise ConfigManagerNotLoadedException('call .load() on ConfigManager before .set()')

        if section_path_str is None:
            section_path_str = self.section.name

        section_path = SectionPath(section_path_str)

        if allow_create:
            self._set_func_or_config_with_create(section_path, value)
        else:
            self._set_func_or_config_no_create(section_path, value)

    def _set_func_or_config_with_create(self, section_path: SectionPath, value: Any):
        obj = self
        section_basepath = self.basepath
        for i, section in enumerate(section_path[:-1]):
            section_basepath = os.path.join(section_basepath, section)
            try:
                obj = getattr(obj, section)
            except KeyError as e:
                new_section = ConfigSection([], name=section)
                obj.append(new_section)
                obj = getattr(obj, section)

        # Now have collection object which should hold this final object
        obj.append(value)

    def _set_func_or_config_no_create(self, section_path: SectionPath, value: Any):
        _set_in_nested_obj_by_section_path(self, section_path, value)

    def _get_default_func_or_section_config(self, section_path_str: str=None,
                                            create: bool = False) -> Union[ActiveFunctionConfig, ConfigSection]:

        if section_path_str is None:
            # local config. Default is blank config
            return ActiveFunctionConfig()
        else:
            # otherwise, load from file for default
            section_path = SectionPath(section_path_str)
            filepath = section_path.to_filepath(self.basepath)

            try:
                config_obj = _get_from_nested_obj_by_section_path(self, section_path)
            except KeyError as e:
                # config object not already created
                if not create:
                    raise e
                config_obj = ActiveFunctionConfig()
            if isinstance(config_obj, ConfigSection):
                return ConfigSection.from_files(filepath)
            if isinstance(config_obj, (ActiveFunctionConfig, ActiveFunctionConfigFile)):
                return ActiveFunctionConfig.from_file(filepath + '.py')
            else:
                raise ValueError(f'expected section path to return ConfigSection or FunctionConfig, '
                                 f'got {config_obj} of type {type(config_obj)}')

    def _is_function_or_pipeline_path(self, section_path_str: str) -> bool:
        section_path = SectionPath(section_path_str)
        # Goes into nested sections, until it pulls the final config or section
        config_or_section: ConfigSectionOrConfig = _get_from_nested_obj_by_section_path(self, section_path)
        if isinstance(config_or_section, ConfigSection):
            # must be section, not individual pipeline or function
            return False
        elif isinstance(config_or_section, (ActiveFunctionConfig, ActiveFunctionConfigFile)):
            # must be individual function as Config is returned
            return True
        else:
            raise ValueError(f'expected Config or ConfigSection, got {config_or_section} of type {config_or_section}')

    def _get_project_config_or_local_config_by_section_path(self, section_path_str: Optional[str]
                                                            ) -> Optional[ActiveFunctionConfig]:
        if section_path_str is not None:
            config_obj = self._get_func_or_section_configs(section_path_str)
        else:
            # If no section passed, update local config
            config_obj = self.local_config

        return config_obj


def _get_config_from_config_or_section(config_or_section: ConfigSectionOrConfig) -> Optional[ActiveFunctionConfig]:
    # Pull Config file from ConfigSection
    if isinstance(config_or_section, ActiveFunctionConfig):
        # config already loaded
        return config_or_section
    if isinstance(config_or_section, ConfigSection):
        # config already loaded
        return config_or_section.config
    if isinstance(config_or_section, ActiveFunctionConfigFile):
        # Load config from file
        return config_or_section.load(ActiveFunctionConfig)

    raise ValueError(f'expected Config or ConfigSection, got {config_or_section} of type {config_or_section}')
