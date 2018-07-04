from typing import Callable

from dero.mixins.repr import ReprMixin
from dero.manager.config.models.manager import ConfigManager, FunctionConfig
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
)
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.config.logic.write import dict_as_function_kwarg_str

class Runner(ReprMixin):
    repr_cols = ['config', 'pipelines']

    def __init__(self, config: ConfigManager, pipelines: PipelineRegistrar):
        self.config = config
        self.pipelines = pipelines

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
                results.append(
                    self._run_section(subsection_path_str)
                )
            elif isinstance(section_or_callable, Callable):
                # run function or pipeline
                results.append(self._run_one_func(subsection_path_str))
            else:
                raise ValueError(f'could not run section {subsection_path_str}. expected PipelineCollection or function,'
                                 f'got {section_or_callable} of type {type(section_or_callable)}')

        return results


    def _run_one_func(self, section_path_str: str) -> Result:
        config = self._get_config(section_path_str)
        func = self._get_func_or_collection(section_path_str)

        # Only pass items in config which are arguments of function
        config_dict = config.for_function(func)

        print(f'Running function {section_path_str}({dict_as_function_kwarg_str(config_dict)})')
        result = func(**config_dict)
        print(f'Result:\n{result}\n')

        return result

    def _get_config(self, section_path_str: str) -> FunctionConfig:
        return self.config.get(section_path_str)

    def _get_func_or_collection(self, section_path_str: str) -> PipelineOrFunctionOrCollection:
        return self.pipelines.get(section_path_str)