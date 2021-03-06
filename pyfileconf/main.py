import ast
import itertools
import sys
import os
import traceback
from collections import defaultdict
from functools import partial

import bdb
import warnings
from copy import deepcopy
from typing import TYPE_CHECKING, Union, List, Callable, Tuple, Optional, Any, Sequence, Type, cast, Dict, Set, \
    Iterator, Iterable

from pyfileconf.basemodels.registrar import Registrar
from pyfileconf.batch import BatchUpdater
from pyfileconf.data.logic.convert import convert_to_empty_obj_if_necessary
from pyfileconf.data.models.collection import SpecificClassCollection
from pyfileconf.data.models.dictconfig import SpecificClassDictConfig
from pyfileconf.debug import pdb_post_mortem_or_passed_debug_fn
from pyfileconf.dictfiles.modify import add_item_into_nested_dict_at_section_path, \
    create_dict_assignment_str_from_nested_dict_with_ast_names, pretty_format_str
from pyfileconf.imports.logic.load.name import get_module_and_name_imported_from
from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.iterate import IterativeRunner
from pyfileconf.logger.logger import logger
from pyfileconf.logic.combine import \
    combine_items_into_list_whether_they_are_lists_or_not_then_extract_from_list_if_only_one_item
from pyfileconf.pipelines.models.collection import PipelineCollection
from pyfileconf.pipelines.models.dictconfig import PipelineDictConfig
from pyfileconf.plugin import manager as plugin_manager
from pyfileconf.views.object import ObjectView

if TYPE_CHECKING:
    from pyfileconf.runner.models.interfaces import RunnerArgs, StrOrView, IterativeResults, IterativeResult

from pyfileconf.config.models.manager import ConfigManager
from pyfileconf.pipelines.models.registrar import PipelineRegistrar
from pyfileconf.pipelines.models.dictfile import PipelineDictFile
from pyfileconf.data.models.registrar import SpecificRegistrar
from pyfileconf.data.models.dictfile import SpecificClassDictFile
from pyfileconf.runner.models.runner import Runner, ResultOrResults
from pyfileconf.imports.models.tracker import ImportTracker
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.exceptions.pipelinemanager import PipelineManagerNotLoadedException, \
    NoPipelineManagerForFilepathException, NoPipelineManagerForSectionPathException
from pyfileconf.logger.bind_stdout import stdout_also_logged
from pyfileconf.interfaces import SpecificClassConfigDict
from pyfileconf import context
from pyfileconf.opts import options


class PipelineManager:
    """
    Main class for managing flow-based programming and configuration.
    """

    def __init__(self, folder: str,
                 name: str= 'project',
                 specific_class_config_dicts: Optional[List[SpecificClassConfigDict]] = None,
                 auto_pdb: Union[bool, Callable] = False, force_continue: bool = False,
                 default_config_folder_name: str = 'defaults'):

        if specific_class_config_dicts is None:
            specific_class_config_dicts = []

        self.folder = folder
        self.pipeline_dict_path = os.path.join(folder, 'pipeline_dict.py')
        self.specific_class_config_dicts = specific_class_config_dicts
        self.specific_class_names = [sc_dict['name'] for sc_dict in specific_class_config_dicts]
        self.default_config_path = os.path.join(self.folder, default_config_folder_name)
        self.name = name
        self.auto_pdb = auto_pdb
        self.force_continue = force_continue

        self._registrars: Optional[Sequence[Registrar]] = None
        self._general_registrar: Optional[PipelineRegistrar] = None

        self._validate_options()
        context.active_managers[self.name] = self
        self._create_project_if_needed()


    def __getattr__(self, item):

        if item == 'runner':
            # must not be defined yet
            raise PipelineManagerNotLoadedException('call PipelineManager.load() before accessing '
                                                    'functions and classes')

        # Must be getting function
        return getattr(self.runner, item)

    def __dir__(self):
        exposed_methods = [
            'run',
            'run_product',
            'run_product_gen',
            'get',
            'update',
            'load',
            'reload',
            'refresh',
            'reset',
        ]
        exposed_attrs = ['name'] + self.specific_class_names
        exposed = exposed_methods + exposed_attrs
        if hasattr(self, '_registrars'):
            skip_methods = [
                'scaffold_config',
                'basepath',
            ]

            # Add specific registrar class dict names
            for registrar in self._registrars:
                if isinstance(registrar, SpecificRegistrar):
                    exposed.append(registrar.name)

            # Add general names to main namespace
            register_attrs = [attr for attr in dir(self._general_registrar) if attr not in exposed + skip_methods]
            exposed += register_attrs
        return exposed

    def run(self, section_path_str_or_list: 'RunnerArgs') -> ResultOrResults:
        """
        Use to run registered pipelines/functions/sections. Pass a single section path or a list
        of section paths. If a list is passed, the return value will also be a list, with each
        result item corresponding to the function at the same index.

        If a path for a section is passed rather than a path for a function or pipeline, a list
        of results will be returned for that section as well. Therefore, calling a high-level
        section will result in a nested list structure of results.

        Args:
            section_path_str_or_list: . separated name of path of function or section, or list thereof.
                similar to how a function would be imported. e.g. 'main.data.summarize.summary_func1'
                or when running multiple functions/sections, e.g.
                    ['main.data', 'main.analysis.reg.1']
                These sections/functions are based on the structure of your pipeline_dict

        Returns: result or list of results

        """
        str_or_list_only: Union[str, List[str]] = self._convert_list_or_single_item_view_or_str_to_strs(
            section_path_str_or_list
        )
        additional_items = plugin_manager.plm.hook.pyfileconf_pre_run(
            section_path_str_or_list=section_path_str_or_list, pm=self
        )
        # Will be converted into list always
        str_or_list_only = combine_items_into_list_whether_they_are_lists_or_not_then_extract_from_list_if_only_one_item(
            str_or_list_only, additional_items
        )

        if options.log_stdout:
            with stdout_also_logged():
                return self._run_depending_on_settings(str_or_list_only)
        else:
            return self._run_depending_on_settings(str_or_list_only)

    def run_product(self, section_path_str_or_list: 'RunnerArgs', config_updates: Sequence[Dict[str, Any]],
                    collect_results: bool = True) -> 'IterativeResults':
        """
        Run one or multiple registered functions/sections multiple times, each time
        updating the config with a combination of the passed config updates.

        Aggregates the updates to each config, then takes the itertools product of all the config
        updates to run the functions with each combination of the configs.

        :param section_path_str_or_list: . separated name of path of function or section, or list thereof.
            similar to how a function would be imported. e.g. 'main.data.summarize.summary_func1'
            or when running multiple functions/sections, e.g. ['main.data', 'main.analysis.reg.1']
        :param config_updates: list of kwarg dictionaries which would normally be provided to .update
        :param collect_results: Whether to aggregate and return results, set to False to save memory
            if results are stored in some other way
        :return:
        """
        iterative_runner = IterativeRunner(
            section_path_str_or_list,
            config_updates,
            base_section_path_str=self.name,
            strip_manager_from_iv=True,
        )
        return iterative_runner.run(collect_results=collect_results)

    def run_product_gen(
        self, section_path_str_or_list: 'RunnerArgs', config_updates: Sequence[Dict[str, Any]],
    ) -> Iterator['IterativeResult']:
        iterative_runner = IterativeRunner(
            section_path_str_or_list,
            config_updates,
            base_section_path_str=self.name,
            strip_manager_from_iv=True,
        )
        return iterative_runner.run_gen()


    def _run_depending_on_settings(self, section_path_str_or_list: Union[str, List[str]]) -> ResultOrResults:
        if self.auto_pdb:
            return self._run_with_auto_pdb(section_path_str_or_list)

        if self.force_continue:
            return self._run_with_force_continue(section_path_str_or_list)

        return self.runner.run(section_path_str_or_list)

    def _run_with_auto_pdb(self, section_path_str_or_list: 'RunnerArgs'):
        pm_func = partial(pdb_post_mortem_or_passed_debug_fn, debug_fn=self.auto_pdb)

        result, successful = _try_except_run_func_except_user_interrupts(
            self.runner.run,
            except_func=pm_func,
            try_func_kwargs=dict(
                section_path_str_or_list=section_path_str_or_list
            ),
        )

        if successful:
            return result
        else:
            return None

    def _run_with_force_continue(self, section_path_str_or_list: Union[str, List[str]]):
        if not isinstance(section_path_str_or_list, list):
            section_path_str_or_list = [section_path_str_or_list]
            strip_list_at_end = True
        else:
            strip_list_at_end = False

        exceptions: List[RunnerException] = []
        results = []

        for section_path_str in section_path_str_or_list:
            result, successful = _try_except_run_func_except_user_interrupts(
                self.runner.run,
                except_func=_return_with_traceback,
                try_func_kwargs=dict(
                    section_path_str_or_list=section_path_str
                ),
                print_traceback=False
            )
            if successful:
                results.append(result)
            else:
                exception, tb = result
                re = RunnerException(
                    exception,
                    section_path_str=section_path_str,
                    trace_back=tb
                )
                exceptions.append(re)
                logger.error(re)
        report_runner_exceptions(exceptions)

        if strip_list_at_end:
            if len(results) == 0:
                return []
            elif len(results) > 1:
                raise ValueError('should not have multiple results')
            return results[0]
        else:
            return results

    # TODO [#13]: multiple section path strs
    def get(self, section_path_str_or_view: 'StrOrView'):
        section_path_str = self._get_section_path_str_from_section_path_str_or_view(section_path_str_or_view)
        return self.runner.get(section_path_str)

    def reset(self, section_path_str_or_view: 'StrOrView', allow_create: bool = False):
        """
        Resets a function or section config to default.

        To reset all configs, use .reload() instead.

        :param section_path_str_or_view:
        :return:
        """
        logger.info(f'Resetting config for {section_path_str_or_view}')
        section_path_str = self._get_section_path_str_from_section_path_str_or_view(section_path_str_or_view)
        self.runner.reset(section_path_str, allow_create=allow_create)
        logger.debug(f'Finished resetting config for {section_path_str_or_view}')

    def reload(self) -> None:
        """
        Useful for getting file system changes without having to start a new Python session. Also resets
        any locally defined configuration.

        Reloads functions from pipeline dict, scaffolds config files for any new functions,
        and updates configuration from files.

        Returns: None

        """
        logger.info(f'Reloading {self.name}')
        self._wipe_loaded_modules()
        self.load()
        logger.debug(f'Finished reloading {self.name}')

    def load(self) -> None:
        """
        Wrapper to track imported modules so that can reimport them upon reloading
        """
        logger.debug(f'Running load for {self.name}')
        self._import_tracker = ImportTracker()

        try:
            self._load_pipeline_config_and_runner()
        except Exception as e:
            # Reset loaded modules from import, completely canceling load so it can be tried again
            self._loaded_modules = self._import_tracker.imported_modules
            self._wipe_loaded_modules()
            self._loaded_modules = [] # modules have been wiped, must be sure they won't be wiped again
            raise e

        self._loaded_modules = self._import_tracker.imported_modules
        logger.debug(f'Finished running load for {self.name}')

    def update(self, d_: dict=None, section_path_str: str=None, pyfileconf_persist: bool = True, **kwargs):
        """
        Update the configuration for an item by section path.

        The main logic is in _update but this also calls the
        pyfileconf_pre_update and pyfileconf_post_update hooks

        :param d_: dictionary of updates
        :param section_path_str: section path of item to be updated
        :param pyfileconf_persist: whether to make changes last through refreshing config
        :param kwargs: kwarg updates
        :return:
        """
        new_updates_list: List[Dict[str, Any]] = plugin_manager.plm.hook.pyfileconf_pre_update(
            pm=self, d_=d_, section_path_str=section_path_str, kwargs=kwargs
        )
        new_updates_dict: Dict[str, Any] = {k: v for d in new_updates_list for k, v in d.items()}
        if new_updates_dict:
            if d_ is not None:
                d_.update(new_updates_dict)
            kwargs.update(new_updates_dict)

        self._update(d_, section_path_str=section_path_str, pyfileconf_persist=pyfileconf_persist, **kwargs)

        plugin_manager.plm.hook.pyfileconf_post_update(
            pm=self, d_=d_, section_path_str=section_path_str, kwargs=kwargs
        )

    def update_batch(self, updates: Iterable[dict]):
        """
        Update the configuration for an multiple items by section path.

        The main logic is just calling _update in a loop but this also calls the
        pyfileconf_pre_update_batch and pyfileconf_post_update_batch hooks

        :param updates: iterable of dictionaries of config updates
        :return: None
        """
        updater = BatchUpdater(
            base_section_path_str=self.name,
            strip_manager_from_iv=True,
        )
        updater.update(updates)

    def _update(self, d_: dict=None, section_path_str: str=None, pyfileconf_persist: bool = True, **kwargs):
        """
        Update the configuration for an item by section path

        :param d_: dictionary of updates
        :param section_path_str: section path of item to be updated
        :param pyfileconf_persist: whether to make changes last through refreshing config
        :param kwargs: kwarg updates
        :return:
        """
        from pyfileconf.selector.models.itemview import is_item_view

        all_updates = {}
        if d_ is not None:
            all_updates.update(d_)
        all_updates.update(kwargs)
        logger.info(f'Updating {section_path_str} with config: {all_updates}')

        if section_path_str:
            # If any of the updates are putting an ItemView as the value, then
            # record that this config is dependent on the config referenced
            # by the ItemView
            all_updates = {**kwargs}
            if d_ is not None:
                all_updates.update(d_)
            full_sp = SectionPath.join(self.name, section_path_str)
            for value in all_updates.values():
                if is_item_view(value):
                    context.add_config_dependency(full_sp, value)

        self.runner.update(d_, section_path_str, pyfileconf_persist=pyfileconf_persist, **kwargs)
        logger.debug(f'Finished updating {section_path_str} with config: {all_updates}')

    def refresh(self, section_path_str: str):
        """
        Reloads from the existing file, then reapplies any config updates. Useful for when
        this config depends on the attribute of some other config which was updated.

        :param section_path_str: section path of item to be refreshed
        :return:
        """
        logger.info(f'Refreshing config for {section_path_str}')
        self.runner.refresh(section_path_str)
        logger.debug(f'Finished refreshing config for {section_path_str}')

    def create(self, section_path_str: str, func_or_class: Optional[Union[Callable, Type]] = None):
        """
        Create a new configuration entry dynamically rather than manually modifying dict file

        :param func_or_class: function or class to use to generate config
        :param section_path_str: section path at which the config should be stored
        :return:
        """
        logger.info(f'Creating config for {section_path_str}')
        section_path = SectionPath(section_path_str)

        if section_path[0] in self.specific_class_names:
            # Got path for a specific class dict, add to specific class dict
            if len(section_path) < 3:
                raise ValueError('when targeting a specific class dict, section path must have minimum length of '
                                 '3, e.g. example_class.thing.stuff')
            if func_or_class is not None:
                raise ValueError('only pass func_or_class when targeting main pipeline dict, not specific class dict')
            self._create_specific_class_dict_entry(section_path)
            full_sp = section_path
            registrar = self._registrar_dict[section_path[0]]
            klass = registrar.collection.klass
            if klass is None:
                raise ValueError(f'must have specific class set, got None for class in {registrar}')
            key_attr = registrar.collection.key_attr
            registrar_obj = convert_to_empty_obj_if_necessary(section_path[-1], klass, key_attr=key_attr)
            set_section_path_str = SectionPath.from_section_str_list(section_path[1:-1]).path_str
            scaffold_path_str = SectionPath.from_section_str_list(section_path[1:]).path_str
        else:
            # Got path for main pipeline dict, add to main pipeline dict
            if func_or_class is None:
                raise ValueError('when adding creating item in main pipeline dict, must pass function or class')
            self._create_pipeline_dict_entry(section_path, func_or_class)
            name = func_or_class.__name__
            full_sp = SectionPath.join(section_path, name)
            mod, import_base = get_module_and_name_imported_from(func_or_class)
            obj_import = ObjectImportStatement([name], import_base)
            item = ast.Name(id=name)
            imports = ImportStatementContainer([obj_import])
            registrar_obj = ObjectView.from_ast_and_imports(item, imports)
            if self._general_registrar is None:
                raise ValueError('general registrar must be defined')
            registrar = self._general_registrar
            set_section_path_str = section_path_str
            scaffold_path_str = full_sp.path_str

        registrar.set(set_section_path_str, registrar_obj)
        registrar.scaffold_config_for(scaffold_path_str)
        self.reset(full_sp.path_str, allow_create=True)
        logger.debug(f'Finished creating config for {section_path_str}')

    @classmethod
    def get_manager_by_filepath(cls, filepath: str) -> 'PipelineManager':
        """
        Gets the active pipeline manager which references the passed
        filepath.

        :param filepath:
        :return:
        :raises NoPipelineManagerForFilepathException: When no active pipeline
            manager has a config file matching the file path
        """
        abs_filepath = os.path.abspath(filepath)
        for manager in context.active_managers.values():
            manager_path = os.path.abspath(manager.folder)
            if abs_filepath.startswith(manager_path + os.sep):
                return manager

        raise NoPipelineManagerForFilepathException

    @classmethod
    def get_manager_by_section_path_str(cls, section_path_str: str) -> 'PipelineManager':
        """
        Gets the active pipeline manager which references the passed
        section path.

        :param filepath:
        :return:
        :raises NoPipelineManagerForSectionPathException: When no active pipeline
            manager has a config file matching the file path
        """
        section_path = SectionPath(section_path_str)
        manager_name = section_path[0]
        try:
            manager = context.active_managers[manager_name]
            return manager
        except KeyError:
            raise NoPipelineManagerForSectionPathException


    def _create_specific_class_dict_entry(self, section_path: SectionPath):
        name = section_path[0]
        file_path = os.path.join(self.folder, f'{name}_dict.py')
        specific_class_dict_file = SpecificClassDictFile(file_path, name=name + '_dict')
        specific_dict = specific_class_dict_file.load()

        # Modify specific class dict to add entry
        add_item_into_nested_dict_at_section_path(
            specific_dict,
            # skip first section as that is name of specific class, skip last section as
            # that's name which should be created
            section_path[1:-1],
            str(section_path[-1]),  # last section is name that should be created
            add_as_ast_name=False
        )
        specific_dict_str = pretty_format_str('class_dict = ' + str(specific_dict))

        specific_class_dict_config = SpecificClassDictConfig(
            dict(class_dict=specific_dict_str),
            name='specific_class_dict',
            _file=specific_class_dict_file,
        )
        specific_class_dict_file.save(specific_class_dict_config)

    def _create_pipeline_dict_entry(self, section_path: SectionPath, func_or_class: Union[Callable, Type]):
        pipeline_dict_file = PipelineDictFile(self.pipeline_dict_path, name='pipeline_dict')
        pipeline_dict = pipeline_dict_file.load()

        mod, import_base = get_module_and_name_imported_from(func_or_class)
        obj_import = ObjectImportStatement([func_or_class.__name__], import_base)
        imports = ImportStatementContainer([obj_import])

        # Modify pipeline dict to add entry
        add_item_into_nested_dict_at_section_path(pipeline_dict, section_path, func_or_class.__name__)

        # Convert pipeline dict to string for output
        pipeline_dict_str = create_dict_assignment_str_from_nested_dict_with_ast_names(pipeline_dict)

        pipeline_dict_config = PipelineDictConfig(
            dict(pipeline_dict=pipeline_dict_str),
            name='pipeline_dict',
            _file=pipeline_dict_file,
            imports=imports
        )
        pipeline_dict_file.save(pipeline_dict_config)


    def _load_pipeline_config_and_runner(self) -> None:
        """
        External logic for main initialization
        Returns:

        """
        # Load dynamically instead of passing dict to ensure modules are loaded into sys now
        self._registrars, self._general_registrar = create_registrars(
            self.specific_class_config_dicts,
            self.default_config_path,
            self.folder,
            self.pipeline_dict_path,
            manager_name=self.name,
        )

        self.config = ConfigManager(self.default_config_path, self.name)
        self.config.load()

        self.runner = Runner(
            config=self.config,
            registrars=self._registrars,
            general_registrar=self._general_registrar,
            name=self.name,
        )

    def _wipe_loaded_modules(self):
        [sys.modules.pop(module) for module in self._loaded_modules]

    def _convert_list_or_single_item_view_or_str_to_strs(self, run_list: 'RunnerArgs') -> Union[str, List[str]]:
        if isinstance(run_list, list):
            return [self._get_section_path_str_from_section_path_str_or_view(run_arg) for run_arg in run_list]
        else:
            return self._get_section_path_str_from_section_path_str_or_view(run_list)

    def _get_section_path_str_from_section_path_str_or_view(self,section_path_str_or_view: 'StrOrView') -> str:
        from pyfileconf.selector.models.itemview import is_item_view
        if is_item_view(section_path_str_or_view):
            # ItemView will have PipelineManager.name as first section, must strip
            section_path = SectionPath(section_path_str_or_view.section_path_str)  # type: ignore
            relative_section_path = SectionPath.from_section_str_list(section_path[1:])
            return relative_section_path.path_str
        elif isinstance(section_path_str_or_view, str):
            return section_path_str_or_view
        else:
            raise ValueError(f'expected str or ItemView. Got {section_path_str_or_view} of '
                             f'type {type(section_path_str_or_view)}')

    def _validate_options(self):
        if self.auto_pdb and self.force_continue:
            raise ValueError('cannot force continue and drop into pdb at the same time')
        if self.name in context.active_managers:
            warnings.warn(f'should not repeat names of PipelineManagers. Got repeated name {self.name}. '
                          f'The original PipelineManager has been replaced in the Selector.')

    def _create_project_if_needed(self):
        if self._need_to_create_project():
            create_project(self.folder, options.log_folder, self.specific_class_config_dicts)

    def _need_to_create_project(self) -> bool:
        return any([
            not os.path.exists(self.folder),
            not os.path.exists(self.pipeline_dict_path),
            not os.path.exists(self.default_config_path),
            options.log_folder is not None and not os.path.exists(options.log_folder),
            *[
                not os.path.exists(path) for path in
                [os.path.join(self.folder, f'{name}_dict.py') for name in self.specific_class_names]
            ],
        ])

    def __del__(self):
        try:
            current_manager_under_this_key = context.active_managers[self.name]
        except KeyError:
            # Must have already been deleted from active managers, do nothing
            return

        if current_manager_under_this_key is self:
            del context.active_managers[self.name]

    @property
    def _registrar_dict(self) -> Dict[str, Registrar]:
        if self._general_registrar is None:
            raise ValueError('general registrar must be defined')
        rd: Dict[str, Registrar] = {'general': self._general_registrar}
        if self._registrars is not None:
            for registrar in self._registrars:
                rd[registrar.name] = registrar
        return rd


def _try_except_run_func_except_user_interrupts(try_func: Callable, except_func: Callable = lambda x: x,
                                                exceptions: Sequence[Type[BaseException]] = (
                                                        KeyboardInterrupt,
                                                        SystemExit,
                                                        bdb.BdbQuit
                                                ), try_func_kwargs: Optional[dict] = None,
                                                except_func_kwargs: Optional[dict] = None,
                                                print_traceback: bool = True) -> Tuple[Any, bool]:
    """
    Args:
        try_func:
        except_func: first arg of except_func must accept the exception being raised
        exceptions:
        try_func_kwargs:
        except_func_kwargs:

    Returns:
        Tuple where first item is the result and second item is a boolean for whether an exception was raised.
        In the case of passed exceptions being raised, will quit.
        In the case of another exception being raised, the result of except_func will be returned as the first item
        and False will be the second item of the tuple.

    """
    if try_func_kwargs is None:
        try_func_kwargs = {}

    try:
        return try_func(**try_func_kwargs), True
    except exceptions:  # type: ignore
        quit()
    except Exception as e:
        if print_traceback:
            logger.error(traceback.format_exc())
        if except_func_kwargs is None:
            except_result = except_func(e)
        else:
            except_result = except_func(e, **except_func_kwargs)
        return except_result, False

def _return_with_traceback(any: Any) -> Tuple[Any, str]:
    return any, traceback.format_exc()

class RunnerException(Exception):

    def __init__(self, *args, section_path_str: 'StrOrView' = None, trace_back: str = None):
        self.section_path_str = section_path_str
        self.trace_back = trace_back

        if len(args) > 0:
            self.exc = args[0]
        else:
            self.exc = None

        super().__init__(*args)

    def __str__(self):
        output_str = f'Error while running {self.section_path_str}:\n\n'
        output_str += self.trace_back

        return output_str


def report_runner_exceptions(runner_exceptions: List[RunnerException]) -> None:
    if len(runner_exceptions) == 0:
        logger.info('\n\nEverything ran successfully, no exceptions to report.\n\n')
        return

    sp_strs = ', '.join([str(exc.section_path_str) for exc in runner_exceptions])
    full_exc_str = f'Exception summary for running {sp_strs} (exceptions were also shown when raised):\n'
    full_exc_str += '\n\n'.join([str(exc) for exc in runner_exceptions])
    logger.error(full_exc_str)


def create_project(path: str, logs_path: str,
                   specific_class_config_dicts: Optional[List[Dict[str, Union[str, Type, List[str]]]]] = None):
    """
    Creates a new pyfileconf project file structure
    """
    defaults_path = os.path.join(path, 'defaults')
    pipeline_path = os.path.join(path, 'pipeline_dict.py')

    if not os.path.exists(defaults_path):
        os.makedirs(defaults_path)
    if logs_path is not None and not os.path.exists(logs_path):
        os.makedirs(logs_path)
    if not os.path.exists(pipeline_path):
        with open(pipeline_path, 'w') as f:
            f.write('\npipeline_dict = {}\n')
    if specific_class_config_dicts:
        for specific_class_config in specific_class_config_dicts:
            name = specific_class_config['name']
            dict_path = os.path.join(path, f'{name}_dict.py')
            if not os.path.exists(dict_path):
                with open(dict_path, 'w') as f:
                    f.write(f'\nclass_dict = {{}}\n')



def _validate_registrars(registrars: List[SpecificRegistrar], general_registrar: PipelineRegistrar):
    used_names = dir(general_registrar)
    for registrar in registrars:
        if registrar.name in used_names:
            raise ValueError(f'cannot use a name for a specific class dict which is already specified in '
                             f'top-level pipeline_dict. The issue is with {registrar.name}.')

    all_registrar_names = [registrar.name for registrar in registrars]
    if len(set(all_registrar_names)) != len(all_registrar_names):
        raise ValueError(f'cannot have multiple specific class dicts with the same '
                         f'name attribute. Got names: {all_registrar_names}')


def create_registrars(specific_class_config_dicts: List[SpecificClassConfigDict],
                      basepath: str, pipeline_folder: str, pipeline_dict_path: str,
                      manager_name: Optional[str] = None
                      ) -> Tuple[List[SpecificRegistrar], PipelineRegistrar]:
    registrars, general_registrar = _create_registrars_or_collections_from_dict(
        specific_class_config_dicts,
        basepath,
        pipeline_folder,
        pipeline_dict_path,
        registrar=True,
        manager_name=manager_name,
    )
    registrars = cast(List[SpecificRegistrar], registrars)
    general_registrar = cast(PipelineRegistrar, general_registrar)
    _validate_registrars(registrars, general_registrar)
    for registrar in registrars:
        registrar.scaffold_config()
    general_registrar.scaffold_config()

    return registrars, general_registrar


def create_collections(specific_class_config_dicts: List[SpecificClassConfigDict],
                       basepath: str, pipeline_folder: str, pipeline_dict_path: str,
                       manager_name: Optional[str] = None
                       ) -> Tuple[List[SpecificClassCollection], PipelineCollection]:
    collections, general_collection = _create_registrars_or_collections_from_dict(
        specific_class_config_dicts,
        basepath,
        pipeline_folder,
        pipeline_dict_path,
        registrar=False,
        manager_name=manager_name,
    )
    collections = cast(List[SpecificClassCollection], collections)
    general_collection = cast(SpecificRegistrar, general_collection)
    return collections, general_collection


def _create_registrars_or_collections_from_dict(
    specific_class_config_dicts: List[SpecificClassConfigDict],
    basepath: str, pipeline_folder: str, pipeline_dict_path: str, registrar: bool = True,
    manager_name: Optional[str] = None
) -> Tuple[
        Union[List[SpecificRegistrar], List[SpecificClassCollection]],
        Union[PipelineRegistrar, PipelineCollection]
    ]:
    pipeline_class: Union[Type[PipelineRegistrar], Type[PipelineCollection]]
    specific_class_class: Union[Type[SpecificRegistrar], Type[SpecificClassCollection]]
    if registrar:
        pipeline_class = PipelineRegistrar
        specific_class_class = SpecificRegistrar
    else:
        pipeline_class = PipelineCollection
        specific_class_class = SpecificClassCollection

    # Load dynamically instead of passing dict to ensure modules are loaded into sys now
    pipeline_dict_file = PipelineDictFile(pipeline_dict_path, name='pipeline_dict')
    pipeline_dict = pipeline_dict_file.load()

    objs: Union[List[SpecificRegistrar], List[SpecificClassCollection]] = []
    for specific_class_config_dict in specific_class_config_dicts:

        # Set defaults then update with actual config
        config_dict: Dict[str, Optional[Union[str, Type, List[str]]]] = dict(
            always_assign_strs=None,
            always_import_strs=None,
        )
        config_dict.update(specific_class_config_dict)  # type: ignore

        for key in ('name', 'class'):
            if key not in config_dict or config_dict[key] is None:
                raise ValueError(f'{key} is required in {config_dict}')

        # Kwargs require 'klass' while config dict is 'class'
        kwargs_dict = deepcopy(config_dict)
        kwargs_dict['klass'] = config_dict['class']
        kwargs_dict.pop('class')

        name = cast(str, config_dict['name'])
        file_path = os.path.join(pipeline_folder, f'{name}_dict.py')
        specific_class_dict_file = SpecificClassDictFile(file_path, name=name + '_dict')
        specific_dict = specific_class_dict_file.load()
        obj = specific_class_class.from_dict(
            specific_dict,
            basepath=os.path.join(basepath, name),
            imports=specific_class_dict_file.interface.imports,
            **kwargs_dict  # type: ignore
        )
        objs.append(obj)

    general_obj = pipeline_class.from_dict(
        pipeline_dict,
        basepath=basepath,
        name=manager_name,
        imports=pipeline_dict_file.interface.imports
    )
    return objs, general_obj
