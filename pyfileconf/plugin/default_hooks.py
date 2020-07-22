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
