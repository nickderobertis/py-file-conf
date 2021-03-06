import inspect
from typing import Callable, Tuple, cast, Sequence, Type, Union, Dict, Any, List
from functools import partial

from mixins.repr import ReprMixin

from pyfileconf.basemodels.collection import Collection
from pyfileconf.basemodels.registrar import Registrar
from pyfileconf.config.logic.apply import apply_config
from pyfileconf.config.models.manager import ConfigManager, ActiveFunctionConfig
from pyfileconf.data.models.collection import SpecificClassCollection
from pyfileconf.exceptions.config import ConfigManagerNotLoadedException
from pyfileconf.logger.logger import logger
from pyfileconf.pipelines.models.registrar import PipelineRegistrar, PipelineCollection
from pyfileconf.logic.get import _get_public_name_or_special_name
from pyfileconf.plugin import manager
from pyfileconf.runner.models.interfaces import (
    StrOrListOfStrs,
    Result,
    Results,
    ResultOrResults
)
from pyfileconf.pipelines.models.interfaces import (
    FunctionOrCollection,
)
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.config.logic.write import dict_as_function_kwarg_str
from pyfileconf.pmcontext.tracing import StackTracker
from pyfileconf.views.object import ObjectView

class Runner(ReprMixin):
    repr_cols = ['_config', '_pipelines']

    def __init__(self, config: ConfigManager, registrars: Sequence[Registrar], general_registrar: PipelineRegistrar,
                 name: str):
        self._config = config
        self._registrars = registrars
        self._general_registrar = general_registrar
        self._manager_name = name

        self._full_getattr = ''
        self._all_specific_classes = tuple([registrar.klass for registrar in self._registrars])
        self._specific_class_registrar_map = {registrar.klass: registrar for registrar in self._registrars}
        self._loaded_objects: Dict[str, Any] = {}

    def __getattr__(self, item):
        # TODO [#14]: find way of doing runner look ups with fewer side effects
        # TODO [#15]: find a way to get __getattr__ logic for runner working for sections
        self._full_getattr += item
        try:
            func_or_collection = self._get_func_or_collection(self._full_getattr)
        except KeyError as e:
            self._full_getattr = '' # didn't find an item, must be incorrect path. reset total path
            raise e

        if isinstance(func_or_collection, (PipelineCollection, SpecificClassCollection)):
            # Got section, need to keep going. Return self
            self._full_getattr += '.' # add period to separate next section
            return self
        else:
            # Got function or class, return the function or class itself
            full_getattr = self._full_getattr
            self._full_getattr = ''  # found the item, reset for next time
            configured_func_or_class = self.get(full_getattr)
            return configured_func_or_class

    # TODO [#16]: this may work once __getattr__ works with sections
    # def __dir__(self):
    #     exposed_methods = [
    #         'run',
    #         'get',
    #     ]
    #
    #     if self._full_getattr != '':
    #         # Already into nested runner, need to pull appropriate collection
    #         try:
    #             func_or_collection = self._get_func_or_collection(self._full_getattr)
    #             pipeline_attrs = [attr for attr in dir(func_or_collection) if attr not in exposed_methods]
    #         except KeyError:
    #             pipeline_attrs = []
    #
    #     else:
    #         # Original runner. Just pull pipeline register attrs
    #         pipeline_attrs = [attr for attr in dir(self._pipelines) if attr not in exposed_methods]
    #
    #     return exposed_methods + pipeline_attrs


    def run(self, section_path_str_or_list: StrOrListOfStrs) -> ResultOrResults:
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
        multiple_results = False
        if isinstance(section_path_str_or_list, str):
            # Running single function/class
            result = self._run(section_path_str_or_list)
        elif isinstance(section_path_str_or_list, list):
            multiple_results = True
            result = [self._run(section_path_str) for section_path_str in section_path_str_or_list]
        else:
            raise ValueError('must pass str or list of strs of section paths to Runner.run')

        additional_results = manager.plm.hook.pyfileconf_post_run(results=result, runner=self)
        if additional_results and multiple_results:
            result.extend(additional_results)
        elif additional_results and not multiple_results:
            result = [result, *additional_results]

        return result

    def _run(self, section_path_str: str) -> ResultOrResults:
        """
        Internal run function for running a single section path string. Handles both running
        sections and running individual functions/classes

        Args:
            section_path_str:

        Returns:

        """
        func_or_collection = self._get_func_or_collection(section_path_str)
        if isinstance(func_or_collection, PipelineCollection):
            return self._run_section(section_path_str)
        elif self._is_specific_class(func_or_collection):
            return self._run_one_specific_class(section_path_str)
        elif inspect.isclass(func_or_collection):
            return self._run_one_class(section_path_str)
        elif callable(func_or_collection):
            return self._run_one_func(section_path_str)
        else:
            raise ValueError(f'could not run section {section_path_str}. expected PipelineCollection or function,'
                             f'got {func_or_collection} of type {type(func_or_collection)}')

    def _run_section(self, section_path_str: str) -> Results:
        section = self._get_func_or_collection(section_path_str)
        section = cast(PipelineCollection, section)
        results = []
        for section_or_object_view in section:

            # Get section path by which to call this item
            subsection_name = _get_public_name_or_special_name(section_or_object_view, accept_output_names=False)
            subsection_path_str = SectionPath.join(section_path_str, subsection_name).path_str

            # Get from object view if necessary
            if isinstance(section_or_object_view, ObjectView):
                section_or_callable = section_or_object_view.item
            else:
                section_or_callable = section_or_object_view

            if isinstance(section_or_callable, PipelineCollection):
                # got another section within this section. recursively call run section
                results.append(self._run_section(subsection_path_str))
            elif self._is_specific_class(section_or_callable):
                results.append(self._run_one_specific_class(section_path_str))
            elif inspect.isclass(section_or_callable):
                results.append(self._run_one_class(section_path_str))
            elif callable(section_or_callable):
                # run function
                results.append(self._run_one_func(subsection_path_str))
            else:
                raise ValueError(f'could not run section {subsection_path_str}. expected PipelineCollection or '
                                 f'function or class,'
                                 f'got {section_or_callable} of type {type(section_or_callable)}')

        return results


    def _run_one_func(self, section_path_str: str) -> Result:
        with StackTracker(section_path_str, base_section_path_str=self._manager_name):
            _, config_dict = self._get_func_and_config(section_path_str)
            func = self._get_one_func_with_config(section_path_str)

            logger.info(f'Running function {section_path_str}({dict_as_function_kwarg_str(config_dict)})')
            result = func()
            logger.info(f'Result:\n{result}\n')
        self._add_to_config_dependencies_if_necessary(section_path_str)
        return result

    def _run_one_class(self, section_path_str: str) -> Result:
        with StackTracker(section_path_str, base_section_path_str=self._manager_name):
            klass, config_dict = self._get_func_and_config(section_path_str)
            obj = self._get_one_obj_with_config(section_path_str)

            logger.info(f'Running class {section_path_str}({dict_as_function_kwarg_str(config_dict)})')
            result = obj()
            logger.info(f'Result:\n{result}\n')
        self._add_to_config_dependencies_if_necessary(section_path_str)
        return result

    def _run_one_specific_class(self, section_path_str: str) -> Result:
        with StackTracker(section_path_str, base_section_path_str=self._manager_name):
            klass, config_dict = self._get_class_and_config(section_path_str)
            obj = self._get_one_obj_with_config(section_path_str)
            registrar = self._specific_class_registrar_map[klass]
            execute_attr = registrar.execute_attr
            func = getattr(obj, execute_attr)

            logger.info(f'Running class {section_path_str}({dict_as_function_kwarg_str(config_dict)})')
            result = func()
            logger.info(f'Result:\n{result}\n')
        self._add_to_config_dependencies_if_necessary(section_path_str)
        return result

    def get(self, section_path_str: str):
        logger.debug(f'Getting {section_path_str} in runner')
        func_or_collection = self._get_func_or_collection(section_path_str)
        if isinstance(func_or_collection, Collection):
            return self._get_section(section_path_str)
        elif self._is_specific_class(func_or_collection):
            return self._get_one_obj_with_config(section_path_str)
        elif inspect.isclass(func_or_collection):
            return self._get_one_obj_with_config(section_path_str)
        elif callable(func_or_collection):
            return self._get_one_func_with_config(section_path_str)
        else:
            raise ValueError(f'could not get section {section_path_str}. expected PipelineCollection or function,'
                             f'got {func_or_collection} of type {type(func_or_collection)}')

    # TODO [#50]: restructure runner get and run
    #
    # Currently the checks for section, function, specific class are very repetitive across the
    # various get and run functions. Standardize these and offload into a single function.

    def _get_section(self, section_path_str: str):
        section = self._get_func_or_collection(section_path_str)
        section = cast(Collection, section)

        # Need to handle definition structure which can be lists inside dicts or more dicts inside dicts
        # This method will be called recursively on each section. Check to see if there are any sections
        # inside this section. If so, then that section would be defined by a dict key in the definition,
        # and therefore results should be put in a dict. If there are no sections within this section, then
        # a list was used to store the items in this section and so results will be put in a list.
        results: Union[Dict[str, Union[Collection, Any]], List[Any]]
        if any(isinstance(item, Collection) for item in section):
            results = {}
        else:
            results = []

        for section_or_object_view in section:

            # Get from object view if necessary
            if isinstance(section_or_object_view, ObjectView):
                section_or_callable = section_or_object_view.item
            else:
                section_or_callable = section_or_object_view

            # Get section path by which to call this item
            if self._is_specific_class(section_or_callable):
                # If specific class, need to look up which key holds the name
                subsection_name = section.name_for_obj(section_or_object_view)
            else:
                # If in the main dict, or is a collection, the name attribute or function/class name holds the name
                subsection_name = _get_public_name_or_special_name(section_or_object_view, accept_output_names=False)

            subsection_path_str = SectionPath.join(section_path_str, subsection_name).path_str

            if isinstance(section_or_callable, Collection):
                # not expected to hit these, for mypy
                assert isinstance(results, dict)
                assert section_or_callable.name is not None
                # got another section within this section. recursively call get section
                results[section_or_callable.name] = self._get_section(subsection_path_str)
            elif isinstance(results, dict):
                # got a non-collection, but results were defined as a dict. Should only have collections in dict
                raise ValueError(
                    f'section {section_or_object_view.name} has both collections and items, must only '
                    f'have collections if there is at least one collection. '
                    f'Got {section_or_callable} as non-collection.'
                )
            elif self._is_specific_class(section_or_callable):
                results.append(self._get_one_obj_with_config(subsection_path_str))
            elif callable(section_or_callable):
                # get function
                results.append(self._get_one_func_with_config(subsection_path_str))
            else:
                raise ValueError(f'could not get section {subsection_path_str}. expected Collection or '
                                 f'function or specific class,'
                                 f'got {section_or_callable} of type {type(section_or_callable)}')

        return results

    def _get_one_func_with_config(self, section_path_str: str) -> Callable:
        if section_path_str in self._loaded_objects:
            return self._loaded_objects[section_path_str]

        func, config_dict = self._get_func_and_config(section_path_str)

        full_func = partial(func, **config_dict)

        self._add_full_section_path_str_to_obj(section_path_str, full_func)
        self._loaded_objects[section_path_str] = full_func
        self._add_to_config_dependencies_if_necessary(section_path_str)
        return full_func

    def _get_one_obj_with_config(self, section_path_str: str) -> Any:
        if section_path_str in self._loaded_objects:
            return self._loaded_objects[section_path_str]

        obj = self._get_func_or_collection(section_path_str)
        klass, config_dict = self._get_class_and_config(section_path_str)
        if inspect.isclass(obj):
            obj = obj(**config_dict)
        else:
            apply_config(obj, config_dict)

        self._add_full_section_path_str_to_obj(section_path_str, obj)
        self._loaded_objects[section_path_str] = obj
        self._add_to_config_dependencies_if_necessary(section_path_str)

        return obj

    def _get_config(self, section_path_str: str) -> ActiveFunctionConfig:
        config = self._config.get(section_path_str)
        if config is None:
            raise ConfigManagerNotLoadedException('no config to get')
        return config

    def _get_func_or_collection(self, section_path_str: str) -> FunctionOrCollection:
        section_path = SectionPath(section_path_str)
        registrar_name = section_path[0]

        # Check for specific class dict matching name
        for registrar in self._registrars:
            if registrar.name == registrar_name:
                lookup_in_registrar_section_path = SectionPath.from_section_str_list(section_path[1:]).path_str
                if not lookup_in_registrar_section_path:
                    # Was looking up registrar collection itself
                    return registrar.collection
                # Looking up within registrar
                return registrar.get(lookup_in_registrar_section_path)

        # Try to return from general registrar
        return self._general_registrar.get(section_path_str)

        # raise NoRegistrarWithNameException(registrar_name)

    def _get_func_and_config(self, section_path_str: str) -> Tuple[Callable, dict]:
        config = self._get_config(section_path_str)
        func = self._get_func_or_collection(section_path_str)
        func = cast(Callable, func)

        # Only pass items in config which are arguments of function
        config_dict = config.for_function(func)

        return func, config_dict

    def _get_class_and_config(self, section_path_str: str) -> Tuple[Type, dict]:
        config = self._get_config(section_path_str)
        obj = self._get_func_or_collection(section_path_str)
        if inspect.isclass(obj):
            klass = obj
        else:
            klass = obj.__class__
        klass = cast('Type', klass)

        # Only pass items in config which are arguments of function
        config_dict = config.for_function(klass)

        return klass, config_dict

    def update(self, d_: dict=None, section_path_str: str=None, pyfileconf_persist: bool = True, **kwargs):
        new_config, updated = self._config.update(d_, section_path_str, pyfileconf_persist=pyfileconf_persist, **kwargs)

        if updated and section_path_str in self._loaded_objects:
            apply_config(self._loaded_objects[section_path_str], new_config)
            self._config.track_post_update(new_config, section_path_str, d_, **kwargs)

    def reset(self, section_path_str: str=None, allow_create: bool = False) -> None:
        """
        Resets a function or section config to default. If no section_path_str
        is passed, resets local config.
        """
        default, updated = self._config.reset(section_path_str=section_path_str, allow_create=allow_create)
        if updated and section_path_str in self._loaded_objects:
            apply_config(self._loaded_objects[section_path_str], default)
            self._config.track_post_update(default, section_path_str, **default)

    def refresh(self, section_path_str: str):
        config, updated, updates = self._config.refresh(section_path_str)

        if updated and section_path_str in self._loaded_objects:
            config = self._get_config(section_path_str)
            apply_config(self._loaded_objects[section_path_str], config)
            self._config.track_post_update(config, section_path_str, updates)

    def _is_specific_class(self, obj: Any) -> bool:
        return self._all_specific_classes and isinstance(obj, self._all_specific_classes)  # type: ignore

    def _add_to_config_dependencies_if_necessary(self, section_path_str: str):
        from pyfileconf import context
        full_sp = SectionPath.join(self._manager_name, section_path_str)
        context.add_config_dependency_for_currently_running_item_if_exists(full_sp, force_update=True)

    def _add_full_section_path_str_to_obj(self, section_path_str: str, obj: Any):
        full_sp_str = SectionPath.join(self._manager_name, section_path_str).path_str
        obj._section_path_str = full_sp_str

