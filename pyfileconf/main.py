import sys
import os
import traceback
import pdb
import bdb
from typing import TYPE_CHECKING, Union, List, Callable, Tuple, Optional, Any, Sequence, Type

if TYPE_CHECKING:
    from pyfileconf.runner.models.interfaces import RunnerArgs, StrOrView

from pyfileconf.config.models.manager import ConfigManager
from pyfileconf.pipelines.models.registrar import PipelineRegistrar
from pyfileconf.pipelines.models.dictfile import PipelineDictFile
from pyfileconf.data.models.registrar import DataRegistrar
from pyfileconf.data.models.dictfile import DataDictFile
from pyfileconf.runner.models.runner import Runner, ResultOrResults
from pyfileconf.imports.models.tracker import ImportTracker
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.exceptions.pipelinemanager import PipelineManagerNotLoadedException
from pyfileconf.logger import stdout_also_logged


class PipelineManager:
    """
    Main class for managing flow-based programming and configuration.
    """

    def __init__(self, pipeline_dict_path: str, data_dict_path: str, basepath: str, name: str='project',
                 auto_pdb: bool=False, force_continue: bool=False, log_folder: Optional[str] = None):
        self.pipeline_dict_path = pipeline_dict_path
        self.data_dict_path = data_dict_path
        self.basepath = basepath
        self.sources_basepath = os.path.join(basepath, 'sources')
        self.name = name
        self.auto_pdb = auto_pdb
        self.force_continue = force_continue
        self.log_folder = log_folder

        self._validate_options()

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

        if self.log_folder is not None:
            with stdout_also_logged(self.log_folder):
                return self._run_depending_on_settings(section_path_str_or_list)
        else:
            return self._run_depending_on_settings(section_path_str_or_list)

    def _run_depending_on_settings(self, section_path_str_or_list: Union[str, List[str]]) -> ResultOrResults:
        if self.auto_pdb:
            return self._run_with_auto_pdb(section_path_str_or_list)

        if self.force_continue:
            return self._run_with_force_continue(section_path_str_or_list)

        return self.runner.run(section_path_str_or_list)

    def _run_with_auto_pdb(self, section_path_str_or_list: 'RunnerArgs'):
        result, successful = _try_except_run_func_except_user_interrupts(
            self.runner.run,
            except_func=lambda exc: pdb.post_mortem(),
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
                print(re)

        report_runner_exceptions(exceptions)

        if strip_list_at_end:
            return results[0]
        else:
            return results

    # TODO [#13]: multiple section path strs
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
        pipeline_dict_file = PipelineDictFile(self.pipeline_dict_path, name='pipeline_dict')
        pipeline_dict = pipeline_dict_file.load()
        data_dict_file = DataDictFile(self.data_dict_path, name='data_dict')
        data_dict = data_dict_file.load()

        self.register = PipelineRegistrar.from_dict(
            pipeline_dict,
            basepath=self.basepath,
            name=self.name,
            imports=pipeline_dict_file.interface.imports
        )
        self.register.scaffold_config()

        self.config = ConfigManager(self.basepath)
        self.config.load()

        self.sources = DataRegistrar.from_dict(
            data_dict,
            basepath=self.sources_basepath,
            name=self.name,
            imports=data_dict_file.interface.imports
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
        from pyfileconf.selector.models.itemview import _is_item_view
        if _is_item_view(section_path_str_or_view):
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
            traceback.print_exc()
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
    print('\n\n')
    for runner_exception in runner_exceptions:
        print(runner_exception)
        print('\n\n')

    if len(runner_exceptions) == 0:
        print('Everything ran successfully, no exceptions to report.\n\n')