"""
Default behavior to be run on hooks
"""
from typing import Any, Dict, Sequence, List, Tuple, TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:
    from pyfileconf.iterate import IterativeRunner
    from pyfileconf.main import PipelineManager
    from pyfileconf.basemodels.config import ConfigBase
    from pyfileconf.config.models.manager import ConfigManager

from pyfileconf.plugin.impl import hookimpl
from pyfileconf.plugin import manager


@hookimpl
def pyfileconf_iter_get_cases(
    config_updates: Sequence[Dict[str, Any]], runner: "IterativeRunner"
) -> List[Tuple[Dict[str, Any], ...]]:
    """
    Collect user passed casses by section path str then call
    itertools.product to produce the cases

    :param config_updates: list of kwarg dictionaries which would normally be provided to .update
    :return: config cases to be run
    """
    from pyfileconf.iterate import get_config_product

    return get_config_product(config_updates)


@hookimpl
def pyfileconf_iter_update_for_case(
    case: Tuple[Dict[str, Any], ...], runner: "IterativeRunner"
):
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the case
    containing all the updates and actually run the updates, before running
    this case.

    :param case: tuple of kwarg dictionaries which would normally be provided to .update
    :param runner: :class:`IterativeRunner` which has been constructed to call iteration
    :return: None
    """
    from pyfileconf.batch import BatchUpdater

    updated_confs: Sequence[Dict[str, Any]]
    if runner.last_case is not None:
        updated_confs = [conf for conf in case if conf not in runner.last_case]
    else:
        updated_confs = case

    bu = BatchUpdater(
        base_section_path_str=runner.base_section_path_str,
        strip_manager_from_iv=runner.strip_manager_from_iv,
    )
    bu.update(updated_confs)


@hookimpl
def pyfileconf_pre_update_batch(
    pm: "PipelineManager", updates: Iterable[dict],
) -> Iterable[dict]:
    return updates


@hookimpl
def pyfileconf_post_config_changed(
    manager: 'ConfigManager',
    new_config: 'ConfigBase',
    updates: Dict[str, Any],
    section_path_str: str,
) -> None:
    """
    Refresh dependent configs after config change

    :param manager: the config manager in which the changing
        config resides
    :param new_config: the config after any changes
    :param updates: the updates which were made to the config
    :param section_path_str: the section path string which can
        be used to look up the config
    :return: None

    :Notes:

        Only called if the action actually modified the config
    """
    manager.refresh_dependent_configs(section_path_str)