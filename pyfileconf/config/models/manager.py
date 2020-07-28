import os
from typing import Union, Any, Optional, Iterable, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.main import PipelineManager

from mixins.repr import ReprMixin

from pyfileconf.basemodels.config import ConfigBase
from pyfileconf.config.models.file import ActiveFunctionConfigFile
from pyfileconf.exceptions.config import ConfigManagerNotLoadedException, CannotResolveConfigDependenciesException
from pyfileconf.logic.get import _get_from_nested_obj_by_section_path
from pyfileconf.logic.set import _set_in_nested_obj_by_section_path
from pyfileconf.config.models.interfaces import ConfigSectionOrConfig
from pyfileconf.config.models.section import ConfigSection, ActiveFunctionConfig
from pyfileconf.plugin import manager
from pyfileconf.sectionpath.sectionpath import SectionPath


class ConfigManager(ReprMixin):
    repr_cols = ['basepath', 'section']

    def __init__(self, basepath: str, pipeline_manager_name: str, main_section: Optional[ConfigSection] = None):
        self.section = main_section
        self.basepath = basepath
        self.pipeline_manager_name = pipeline_manager_name
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
            'pipeline_manager_name',
        ]
        return exposed_methods + exposed_attrs + list(self.section.config_map.keys())

    def load(self):
        self.section = ConfigSection.from_files(self.basepath)

    def update(
        self, d: dict=None, section_path_str: str=None, pyfileconf_persist: bool = True, **kwargs
    ) -> ConfigBase:
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        if config_obj is None:
            raise ConfigManagerNotLoadedException('no config to update')
        would_update = self._determine_and_track_if_config_would_be_updated(
            config_obj, section_path_str, d, **kwargs
        )
        if would_update:
            config_obj.update(d, pyfileconf_persist=pyfileconf_persist, **kwargs)
        return config_obj

    def refresh(self, section_path_str: str):
        config_obj = self._get_project_config_or_local_config_by_section_path(section_path_str)
        if config_obj is None:
            raise ConfigManagerNotLoadedException('no config to refresh')
        would_refresh = self._determine_and_track_if_config_would_be_refreshed(config_obj, section_path_str)
        if would_refresh:
            config_obj.refresh()

    def refresh_dependent_configs(self, section_path_str: str):
        from pyfileconf import context
        full_sp = SectionPath.join(self.pipeline_manager_name, section_path_str)
        update_deps = {*context.force_update_dependencies[full_sp.path_str]}
        all_updated_deps = set()
        while update_deps:
            _refresh_configs(update_deps)
            all_updated_deps.update(update_deps)
            # Get any newly updated dependencies caused by process of updating dependencies
            new_update_deps = context.force_update_dependencies[full_sp.path_str].difference(all_updated_deps)
            if update_deps == new_update_deps:
                # Not expected, but somehow got stuck in an infinite loop where it is
                # always trying to update the same dependency
                raise CannotResolveConfigDependenciesException(update_deps)
            update_deps = new_update_deps

    def reset(self, section_path_str: str=None, allow_create: bool = False) -> ConfigBase:
        """
        Resets a function or section config to default. If no section_path_str is passed, resets local config.

        To reset all configs, use .load() instead.

        :return: the default configuration

        """
        default = self._get_default_func_or_section_config(section_path_str, create=allow_create)
        self.set(section_path_str, default, allow_create=allow_create)
        return default

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

    def set(self, section_path_str: Optional[str] = None, value: Optional[ConfigBase] = None,
            allow_create: bool = True):
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

        would_update = False
        try:
            current_config = self._get_project_config_or_local_config_by_section_path(section_path_str)
        except KeyError:
            # This is a new config, will always update
            would_update = True
        if not would_update:
            # Not a new config, need to actually determine whether would be updated
            would_update = self._determine_and_track_if_config_would_be_updated(current_config, section_path_str, **value)
        if would_update:
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

    def _track_update(self, config: ConfigBase, section_path_str: str, all_updates: Dict[str, Any]):
        manager.plm.hook.pyfileconf_config_changed(
            manager=self, orig_config=config, updates=all_updates, section_path_str=section_path_str
        )

    def _determine_and_track_if_config_would_be_updated(self, config: ConfigBase, section_path_str: str,
                                                        d: Optional[dict] = None, **updates) -> bool:
        if d is None:
            d = {}

        all_updates = {**d, **updates}
        would_update = config.would_update(all_updates)
        if would_update:
            self._track_update(config, section_path_str, all_updates)
        return would_update

    def _determine_and_track_if_config_would_be_refreshed(self, config: ConfigBase, section_path_str: str) -> bool:
        updates = config.change_from_refresh()
        if updates:
            self._track_update(config, section_path_str, updates)
        return updates != {}

    @property
    def pipeline_manager(self) -> 'PipelineManager':
        from pyfileconf.main import PipelineManager
        return PipelineManager.get_manager_by_section_path_str(self.pipeline_manager_name)


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


def _refresh_configs(section_paths: Iterable[SectionPath]):
    from pyfileconf import PipelineManager

    for sp in section_paths:
        manager = PipelineManager.get_manager_by_section_path_str(sp.path_str)
        relative_section_path = SectionPath('.'.join(sp[1:]))
        manager.refresh(relative_section_path.path_str)