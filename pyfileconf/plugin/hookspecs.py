from typing import Any, Dict, Sequence, List, Tuple

import pluggy

hookspec = pluggy.HookspecMarker("pyfileconf")


@hookspec
def pyfileconf_iter_get_cases(config_updates: Sequence[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], ...]]:
    """
    Called in PipelineManager.run_iter and IterativeRunner to take the user passed
    config updates and return the config cases to be run

    :param config_updates: list of kwarg dictionaries which would normally be provided to .update
    :return: config cases to be run
    """