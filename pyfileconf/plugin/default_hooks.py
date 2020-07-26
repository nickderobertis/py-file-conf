"""
Default behavior to be run on hooks
"""
from typing import Any, Dict, Sequence, List, Tuple, TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:
    from pyfileconf.iterate import IterativeRunner
    from pyfileconf.main import PipelineManager

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

    use_confs: List[Dict[str, Any]] = []
    for conf in updated_confs:
        conf = {**conf, 'pyfileconf_persist': False}
        use_confs.append(conf)

    bu = BatchUpdater(
        base_section_path_str=runner.base_section_path_str,
        strip_manager_from_iv=runner.strip_manager_from_iv,
    )
    sp_strs = [conf['section_path_str'] for conf in use_confs]
    bu.reset(sp_strs)
    bu.update(use_confs)


@hookimpl
def pyfileconf_pre_update_batch(
    pm: "PipelineManager", updates: Iterable[dict],
) -> Iterable[dict]:
    return updates
