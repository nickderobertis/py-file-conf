import sys
import os
from copy import deepcopy

from dero.manager.config.models.manager import ConfigManager
from dero.manager.pipelines.models.registrar import PipelineRegistrar
from dero.manager.runner.models.runner import Runner, StrOrListOfStrs, ResultOrResults
from dero.manager.pipelines.logic.load import pipeline_dict_from_file
from dero.manager.imports.models.tracker import ImportTracker
from dero.manager.sectionpath.sectionpath import SectionPath

class PipelineManager:
    """
    Main class for managing flow-based programming and configuration.
    """

    def __init__(self, pipeline_dict_path: str, basepath: str, name: str='project'):
        self.pipeline_dict_path = pipeline_dict_path
        self.basepath = basepath
        self.name = name

        self._load()

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
        return self.runner.run(section_path_str_or_list)

    def reload(self) -> None:
        """
        Useful for getting file system changes without having to start a new Python session. Also resets
        any locally defined configuration.

        Reloads functions from pipeline dict, scaffolds config files for any new functions,
        and updates configuration from files.

        Returns: None

        """
        self._wipe_loaded_modules()
        self._load()

    def _load(self) -> None:
        """
        Wrapper to track imported modules so that can reimport them upon reloading
        """
        self._import_tracker = ImportTracker()

        self._load_pipeline_config_and_runner()

        self._loaded_modules = self._import_tracker.imported_modules

    def _load_pipeline_config_and_runner(self) -> None:
        """
        External logic for main initialization
        Returns:

        """
        # Add module name to ensure module is loaded into sys
        pipeline_section_path = SectionPath.from_filepath(os.getcwd(), self.pipeline_dict_path)
        pipeline_dict = pipeline_dict_from_file(self.pipeline_dict_path, module_name=pipeline_section_path.path_str)

        imported_modules = self._import_tracker.imported_modules
        imported_modules.reverse() # start with pipeline dict file first, then look at others for imports

        self.register = PipelineRegistrar.from_pipeline_dict(
            pipeline_dict,
            basepath=self.basepath,
            name=self.name,
            loaded_modules=imported_modules
        )
        self.register.scaffold_config()

        self.config = ConfigManager(self.basepath)
        self.config.load()

        self.runner = Runner(config=self.config, pipelines=self.register)

    def _wipe_loaded_modules(self):
        [sys.modules.pop(module) for module in self._loaded_modules]

