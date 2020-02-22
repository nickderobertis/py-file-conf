from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from pyfileconf.main import PipelineManager

from pyfileconf.selector.logic.get.fromglobs import get_dict_of_pipeline_manager_names_and_instances_from_globals
from pyfileconf.selector.logic.get.globs import iter_globals


def get_dict_of_any_defined_pipeline_manager_names_and_instances() -> Dict[str, 'PipelineManager']:
    pm_dict = {}
    for globs in iter_globals():
        pm_dict.update(get_dict_of_pipeline_manager_names_and_instances_from_globals(globs=globs))

    return pm_dict
