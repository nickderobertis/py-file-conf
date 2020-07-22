"""
Contains the hooks which may be attached to in creating plugins
"""
from typing import Any, Dict, Sequence, List, Tuple, Optional, TYPE_CHECKING

from pyfileconf.runner.models.runner import Runner

if TYPE_CHECKING:
    from pyfileconf.main import PipelineManager
    from pyfileconf.iterate import IterativeRunner

import pluggy

from pyfileconf.runner.models.interfaces import RunnerArgs, ResultOrResults

hookspec = pluggy.HookspecMarker("pyfileconf")


@hookspec
def pyfileconf_iter_get_cases(
    config_updates: Sequence[Dict[str, Any]], runner: "IterativeRunner",
) -> List[Tuple[Dict[str, Any], ...]]:
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the user passed
    config updates and return the config cases to be run

    :param config_updates: list of kwarg dictionaries which would normally be provided to .update
    :param runner: :class:`IterativeRunner` which has been constructed to call iteration
    :return: config cases to be run
    """


@hookspec
def pyfileconf_iter_modify_cases(
    cases: List[Tuple[Dict[str, Any], ...]], runner: "IterativeRunner"
):
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the collected
    config cases to be run and modify them in place.

    :param cases: list of tuples of kwarg dictionaries which would normally be provided to .update
    :param runner: :class:`IterativeRunner` which has been constructed to call iteration
    :return: None
    """


@hookspec
def pyfileconf_pre_run(
    section_path_str_or_list: RunnerArgs, pm: "PipelineManager"
) -> Optional[RunnerArgs]:
    """
    Called at the beginning of PipelineManager.run. Can optionally return
    additional section paths to run. If section_path_str_or_list is a
    list then it can also be modified in place.

    :param section_path_str_or_list: section paths which were passed to
        PipelineManager.run
    :param pm: The manager responsible for the run
    :return: additional sections/functions to run, if any
    """


@hookspec
def pyfileconf_post_run(
    results: ResultOrResults, runner: Runner
) -> Optional[ResultOrResults]:
    """
    Called at the end of PipelineManager.run. Can optionally return
    additional results which will be appended to the results list. If results is mutable
    then it can also be modified in place.

    :param results: results from running section/function
    :param runner: :class:`Runner` which has been called to run function/section
    :return: additional results, if any
    """


@hookspec
def pyfileconf_pre_update(
    pm: "PipelineManager",
    d: dict = None,
    section_path_str: str = None,
    kwargs: Dict[str, Any] = None,
) -> Optional[Dict[str, Any]]:
    """
    Called at the beginning of PipelineManager.update. Can optionally return
    a dictionary of updates which will be used to update the passed dictionary.
    Can also modify the passed dictionaries in place.

    :param pm: The manager responsible for the run
    :param d: dictionary of config updates
    :param section_path_str: section path of config to be updated
    :param kwargs: dictionary of config updates
    :return: optional updates to config updates
    """


@hookspec
def pyfileconf_post_update(
    pm: "PipelineManager",
    d: dict = None,
    section_path_str: str = None,
    kwargs: Dict[str, Any] = None,
):
    """
    Called at the end of PipelineManager.update.

    :param pm: The manager responsible for the run
    :param d: dictionary of config updates
    :param section_path_str: section path of config which was updated
    :param kwargs: dictionary of config updates
    :return: None
    """
