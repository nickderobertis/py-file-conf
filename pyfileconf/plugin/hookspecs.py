"""
Contains the hooks which may be attached to in creating plugins
"""
from typing import Any, Dict, Sequence, List, Tuple, Optional

import pluggy

from pyfileconf.runner.models.interfaces import RunnerArgs, ResultOrResults

hookspec = pluggy.HookspecMarker("pyfileconf")


@hookspec
def pyfileconf_iter_get_cases(
    config_updates: Sequence[Dict[str, Any]]
) -> List[Tuple[Dict[str, Any], ...]]:
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the user passed
    config updates and return the config cases to be run

    :param config_updates: list of kwarg dictionaries which would normally be provided to .update
    :return: config cases to be run
    """


@hookspec
def pyfileconf_iter_modify_cases(cases: List[Tuple[Dict[str, Any], ...]]):
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the collected
    config cases to be run and modify them in place.

    :param cases: list of tuples of kwarg dictionaries which would normally be provided to .update
    :return: None
    """


@hookspec
def pyfileconf_pre_run(section_path_str_or_list: RunnerArgs) -> Optional[RunnerArgs]:
    """
    Called at the beginning of PipelineManager.run. Can optionally return
    additional section paths to run. If section_path_str_or_list is a
    list then it can also be modified in place.

    :param section_path_str_or_list: section paths which were passed to
        PipelineManager.run
    :return: additional sections/functions to run, if any
    """


@hookspec
def pyfileconf_post_run(results: ResultOrResults) -> Optional[ResultOrResults]:
    """
    Called at the end of PipelineManager.run. Can optionally return
    additional results which will be appended to the results list. If results is mutable
    then it can also be modified in place.

    :param results: results from running section/function
    :return: additional results, if any
    """
