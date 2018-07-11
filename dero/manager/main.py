import sys
import os
from copy import deepcopy
from typing import TYPE_CHECKING, Union, List
if TYPE_CHECKING:
    from dero.manager.selector.models.itemview import ItemView
    StrOrView = Union[str, ItemView]
    RunnerArgs = Union[str, List[str], ItemView, List[ItemView]]

from dero.manager.config.models.manager import ConfigManager
from dero.manager.pipelines.models.registrar import PipelineRegistrar
from dero.manager.data.models.registrar import DataRegistrar
from dero.manager.runner.models.runner import Runner, StrOrListOfStrs, ResultOrResults
from dero.manager.logic.load import get_pipeline_dict_and_data_dict_from_filepaths
from dero.manager.imports.models.tracker import ImportTracker
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.exceptions.pipelinemanager import PipelineManagerNotLoadedException


class PipelineManager:
    """
    Main class for managing flow-based programming and configuration.
    """

    def __init__(self, pipeline_dict_path: str, data_dict_path: str, basepath: str, name: str='project'):
        self.pipeline_dict_path = pipeline_dict_path
        self.data_dict_path = data_dict_path
        self.basepath = basepath
        self.sources_basepath = os.path.join(basepath, 'sources')
        self.name = name


    def __getattr__(self, item):

        if item in ('runner', 'sources'):
            # must not be defined yet
            raise PipelineManagerNotLoadedException('call PipelineManager.load() before accessing '
                                                    'functions or data sources')

        # Must be getting function
        return getattr(self.runner, item)

    def __dir__(self):
        exposed_methods = [
            'run',
            'get',
            'load',
            'reload'
        ]
        exposed_attrs = ['sources', 'name']
        exposed = exposed_methods + exposed_attrs
        if hasattr(self, 'register'):
            skip_methods = [
                'scaffold_config',
                'basepath',
            ]
            register_attrs = [attr for attr in dir(self.register) if attr not in exposed + skip_methods]
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
        section_path_str_or_list = self._convert_list_or_single_item_view_or_str_to_strs(section_path_str_or_list)
        return self.runner.run(section_path_str_or_list)

    # TODO: multiple section path strs
    def get(self, section_path_str_or_view: 'StrOrView'):
        section_path_str = self._get_section_path_str_from_section_path_str_or_view(section_path_str_or_view)
        section_path = SectionPath(section_path_str)

        if section_path[0] == 'sources':
            return self.sources.get(section_path_str)
        else:
            return self.runner.get(section_path_str)

    def reload(self) -> None:
        """
        Useful for getting file system changes without having to start a new Python session. Also resets
        any locally defined configuration.

        Reloads functions from pipeline dict, scaffolds config files for any new functions,
        and updates configuration from files.

        Returns: None

        """
        self._wipe_loaded_modules()
        self.load()

    def load(self) -> None:
        """
        Wrapper to track imported modules so that can reimport them upon reloading
        """
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

    def _load_pipeline_config_and_runner(self) -> None:
        """
        External logic for main initialization
        Returns:

        """
        # Load dynamically instead of passing dict to ensure modules are loaded into sys now
        pipeline_dict, data_dict = get_pipeline_dict_and_data_dict_from_filepaths(
            self.pipeline_dict_path, self.data_dict_path
        )

        imported_modules = self._import_tracker.imported_modules
        imported_modules.reverse() # start with pipeline dict file first, then look at others for imports

        self.register = PipelineRegistrar.from_dict(
            pipeline_dict,
            basepath=self.basepath,
            name=self.name,
            loaded_modules=imported_modules
        )
        self.register.scaffold_config()

        self.config = ConfigManager(self.basepath)
        self.config.load()

        self.sources = DataRegistrar.from_dict(
            data_dict,
            basepath=self.sources_basepath,
            name=self.name,
            loaded_modules=imported_modules
        )
        self.sources.scaffold_config()

        self.runner = Runner(config=self.config, pipelines=self.register)

    def _wipe_loaded_modules(self):
        [sys.modules.pop(module) for module in self._loaded_modules]

    def _convert_list_or_single_item_view_or_str_to_strs(self, run_list: 'RunnerArgs') -> Union[str, List[str]]:
        if isinstance(run_list, list):
            return [self._get_section_path_str_from_section_path_str_or_view(run_arg) for run_arg in run_list]
        else:
            return self._get_section_path_str_from_section_path_str_or_view(run_list)

    def _get_section_path_str_from_section_path_str_or_view(self,section_path_str_or_view: 'StrOrView') -> str:
        from dero.manager.selector.models.itemview import ItemView
        if isinstance(section_path_str_or_view, ItemView):
            # ItemView will have PipelineManager.name as first section, must strip
            section_path = SectionPath(section_path_str_or_view.section_path_str)
            relative_section_path = SectionPath.from_section_str_list(section_path[1:])
            return relative_section_path.path_str
        elif isinstance(section_path_str_or_view, str):
            return section_path_str_or_view
        else:
            raise ValueError(f'expected str or ItemView. Got {section_path_str_or_view} of '
                             f'type {type(section_path_str_or_view)}')
