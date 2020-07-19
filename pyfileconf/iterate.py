import itertools
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict, Any, Tuple, Sequence


def get_config_product(config_dicts: Sequence[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], ...]]:
    """

    :param config_dicts:
    :return:

    :Examples:

        >>> cd = dict(
        ...     section_path_str='abc',
        ...     a=10
        ... )
        >>> cd2 = dict(
        ...     section_path_str='abc',
        ...     a=20
        ... )
        >>> cd3 = dict(
        ...     section_path_str='def',
        ...     a=20
        ... )
        >>> cds = [cd, cd2, cd3]
        >>> result = get_config_product(cds)
        >>> result
        ... [({'section_path_str': 'abc', 'a': 10}, {'section_path_str': 'def', 'a': 20}),
        ... ({'section_path_str': 'abc', 'a': 20}, {'section_path_str': 'def', 'a': 20})]
    """
    by_section_path_dict = _get_configs_by_section_path_dict(config_dicts)
    return list(itertools.product(*by_section_path_dict.values()))


def _get_configs_by_section_path_dict(config_dicts: Sequence[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """

    :param config_dicts:
    :return:

    :Examples:

        >>> cd = dict(
        ...     section_path_str='abc',
        ...     a=10
        ... )
        >>> cd2 = dict(
        ...     section_path_str='abc',
        ...     a=20
        ... )
        >>> cd3 = dict(
        ...     section_path_str='def',
        ...     a=20
        ... )
        >>> cds = [cd, cd2, cd3]
        >>> result = _get_configs_by_section_path_dict(cds)
        >>> result
        ... {'abc': [{'section_path_str': 'abc', 'a': 10},
        ...       {'section_path_str': 'abc', 'a': 20}],
        ...      'def': [{'section_path_str': 'def', 'a': 20}]})
    """
    combined_dicts = defaultdict(lambda: [])
    for config_dict in config_dicts:
        conf = deepcopy(config_dict)
        sp = conf['section_path_str']
        combined_dicts[sp].append(conf)
    return combined_dicts