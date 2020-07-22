"""
Default behavior to be run on hooks
"""
from typing import Any, Dict, Sequence, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from pyfileconf.iterate import IterativeRunner

from pyfileconf.plugin.impl import hookimpl


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
    from pyfileconf import PipelineManager
    from pyfileconf.sectionpath.sectionpath import SectionPath

    for config_dict in case:
        sp_str = config_dict["section_path_str"]
        if runner.base_section_path_str is not None:
            sp_str = SectionPath.join(
                runner.base_section_path_str, sp_str
            ).path_str
        manager = PipelineManager.get_manager_by_section_path_str(sp_str)
        relative_section_path_str = SectionPath(
            ".".join(SectionPath(sp_str)[1:])
        ).path_str
        manager.reset(relative_section_path_str)
        relative_conf_dict = {**config_dict}
        relative_conf_dict["section_path_str"] = relative_section_path_str
        manager.update(**relative_conf_dict)