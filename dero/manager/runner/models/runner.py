from typing import Callable, Tuple
from functools import partial

from dero.mixins.repr import ReprMixin
from dero.manager.config.models.manager import ConfigManager, ActiveFunctionConfig
from dero.manager.pipelines.models.registrar import PipelineRegistrar, PipelineCollection
from dero.manager.logic.get import _get_public_name_or_special_name
from dero.manager.runner.models.interfaces import (
    StrOrListOfStrs,
    Result,
    Results,
    ResultOrResults
)
from dero.manager.pipelines.models.interfaces import (
    PipelineOrFunctionOrCollection,
    PipelineOrFunction
)
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.config.logic.write import dict_as_function_kwarg_str
from dero.manager.basemodels.pipeline import Pipeline

class Runner(ReprMixin):
    repr_cols = ['_config', '_pipelines']


    def __init__(self, config: ConfigManager, pipelines: PipelineRegistrar):
        self._config = config
        self._pipelines = pipelines
        self._full_getattr = ''

    def __getattr__(self, item):
        # TODO: find way of doing this with fewer side effects
        # TODO: find a way to get this working for sections
        self._full_getattr += item
        try:
            func_or_collection = self._get_func_or_collection(self._full_getattr)
        except KeyError as e:
            self._full_getattr = '' # didn't find an item, must be incorrect path. reset total path
            raise e

        if isinstance(func_or_collection, PipelineCollection):
            # Got section, need to keep going. Return self
            self._full_getattr += '.' # add period to separate next section
            return self
        else:
            # Got function or Pipeline, return the function or pipeline itself
            configured_func_or_pipeline = self.get(self._full_getattr)
            self._full_getattr = ''  # found the item, reset for next time
            return configured_func_or_pipeline

    # TODO: this may work once __getattr__ works with sections
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
        if isinstance(section_path_str_or_list, str):
            # Running single function/pipeline
            return self._run(section_path_str_or_list)
        elif isinstance(section_path_str_or_list, list):
            return [self._run(section_path_str) for section_path_str in section_path_str_or_list]

    def _run(self, section_path_str: str) -> ResultOrResults:
        """
        Internal run function for running a single section path string. Handles both running
        sections and running individual functions/pipelines

        Args:
            section_path_str:

        Returns:

        """
        func_or_collection = self._get_func_or_collection(section_path_str)
        if isinstance(func_or_collection, PipelineCollection):
            return self._run_section(section_path_str)
        elif issubclass(func_or_collection, Pipeline):
            return self._run_one_pipeline(section_path_str)
        elif isinstance(func_or_collection, Callable):
            return self._run_one_func(section_path_str)
        else:
            raise ValueError(f'could not run section {section_path_str}. expected PipelineCollection or function,'
                             f'got {func_or_collection} of type {type(func_or_collection)}')


    def _run_section(self, section_path_str: str) -> Results:
        section: PipelineCollection = self._get_func_or_collection(section_path_str)
        results = []
        for section_or_callable in section:

            # Get section path by which to call this item
            subsection_name = _get_public_name_or_special_name(section_or_callable)
            subsection_path_str = SectionPath.join(section_path_str, subsection_name).path_str

            if isinstance(section_or_callable, PipelineCollection):
                # got another section within this section. recursively call run section
                results.append(self._run_section(subsection_path_str))
            elif isinstance(section_or_callable, Callable):
                # run function
                results.append(self._run_one_func(subsection_path_str))
            elif isinstance(section_or_callable, Pipeline):
                # run pipeline
                results.append(self._run_one_pipeline(subsection_path_str))
            else:
                raise ValueError(f'could not run section {subsection_path_str}. expected PipelineCollection or '
                                 f'function or Pipeline,'
                                 f'got {section_or_callable} of type {type(section_or_callable)}')

        return results


    def _run_one_func(self, section_path_str: str) -> Result:
        func, config_dict = self._get_func_and_config(section_path_str)

        print(f'Running function {section_path_str}({dict_as_function_kwarg_str(config_dict)})')
        result = func(**config_dict)
        print(f'Result:\n{result}\n')

        return result

    def _run_one_pipeline(self, section_path_str: str) -> Result:
        pipeline_class, config_dict = self._get_pipeline_and_config(section_path_str)

        # Construct new pipeline instance with config args
        configured_pipeline = pipeline_class(**config_dict)

        print(f'Running pipeline {configured_pipeline}({dict_as_function_kwarg_str(config_dict)})')
        result = configured_pipeline.execute()
        print(f'Result:\n{result}\n')

        return configured_pipeline

    def get(self, section_path_str: str) -> PipelineOrFunction:
        func_or_collection = self._get_func_or_collection(section_path_str)
        if isinstance(func_or_collection, PipelineCollection):
            # TODO: get sections
            raise NotImplementedError('have not implemented getting sections. works with run')
        elif issubclass(func_or_collection, Pipeline):
            # Got pipeline class
            return self._get_one_pipeline(section_path_str)
        elif isinstance(func_or_collection, Callable):
            return self._get_one_func(section_path_str)
        else:
            raise ValueError(f'could not get section {section_path_str}. expected PipelineCollection or function,'
                             f'got {func_or_collection} of type {type(func_or_collection)}')

    def _get_one_func(self, section_path_str: str) -> Callable:
        func, config_dict = self._get_func_and_config(section_path_str)

        full_func = partial(func, **config_dict)

        return full_func

    def _get_one_pipeline(self, section_path_str: str) -> Pipeline:
        pipeline_class, config_dict = self._get_pipeline_and_config(section_path_str)

        # Construct new pipeline instance with config args
        return pipeline_class(**config_dict)


    def _get_config(self, section_path_str: str) -> ActiveFunctionConfig:
        return self._config.get(section_path_str)

    def _get_func_or_collection(self, section_path_str: str) -> PipelineOrFunctionOrCollection:
        return self._pipelines.get(section_path_str)

    def _get_func_and_config(self, section_path_str: str) -> Tuple[Callable, dict]:
        config = self._get_config(section_path_str)
        func = self._get_func_or_collection(section_path_str)

        # Only pass items in config which are arguments of function
        config_dict = config.for_function(func)

        return func, config_dict

    def _get_pipeline_and_config(self, section_path_str: str) -> Tuple[type, dict]:
        config = self._get_config(section_path_str)
        # pipeline is an instance of the pipeline, without config
        pipeline = self._get_func_or_collection(section_path_str)

        # Only pass items in config which are arguments of function
        config_dict = config.for_function(pipeline.__init__)

        return pipeline, config_dict