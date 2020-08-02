import itertools
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict, Any, Tuple, Sequence, Optional, Iterator

from pyfileconf.basemodels.config import ConfigBase
from pyfileconf.logger.logger import logger
from pyfileconf.plugin import manager
from pyfileconf.runner.models.interfaces import RunnerArgs, IterativeResults, IterativeResult
from pyfileconf.sectionpath.sectionpath import SectionPath


class IterativeRunner:
    """
    Class that enables running functions/sections with different combinations of config updates,
    even across multiple pipeline managers

    Run one or multiple registered functions/sections multiple times, each time
    updating the config with a combination of the passed config updates.

    Aggregates the updates to each config, then takes the itertools product of all the config
    updates to run the functions with each combination of the configs.
    """

    run_items: List[SectionPath]
    config_updates: Sequence[Dict[str, Any]]
    cases: List[Tuple[Dict[str, Any], ...]]
    last_case: Optional[Tuple[Dict[str, Any], ...]] = None
    defaults: Dict[str, Dict[str, Any]]

    def __init__(
        self,
        section_path_str_or_list: RunnerArgs,
        config_updates: Sequence[Dict[str, Any]],
        base_section_path_str: Optional[str] = None,
        strip_manager_from_iv: bool = False,
    ):
        """

        :param section_path_str_or_list: . separated name of path of function or section, or list thereof.
            similar to how a function would be imported. e.g. 'main.data.summarize.summary_func1'
            or when running multiple functions/sections, e.g. ['main.data', 'main.analysis.reg.1']
        :param config_updates: list of kwarg dictionaries which would normally be provided to .update
        :param base_section_path_str: section path str to put at beginning of all passed section paths
        :param strip_manager_from_iv: whether to remove manager name from any incoming item views
        """
        self.base_section_path_str = base_section_path_str
        self.strip_manager_from_iv = strip_manager_from_iv
        self.run_items = SectionPath.list_from_ambiguous(
            section_path_str_or_list,
            base_section_path_str=base_section_path_str,
            strip_manager_from_iv=strip_manager_from_iv,
        )
        self.config_updates = config_updates
        self.cases = self.get_cases()
        self.defaults = self.get_defaults()

    def get_cases(self) -> List[Tuple[Dict[str, Any], ...]]:
        logger.debug('Determining cases for IterativeRunner')
        cases_lol: List[
            List[Tuple[Dict[str, Any], ...]]
        ] = manager.plm.hook.pyfileconf_iter_get_cases(config_updates=self.config_updates, runner=self)
        cases = list(itertools.chain(*cases_lol))
        manager.plm.hook.pyfileconf_iter_modify_cases(cases=cases, runner=self)
        logger.debug(f'Got {cases} for IterativeRunner.cases')
        return cases

    def get_defaults(self) -> Dict[str, Dict[str, Any]]:
        logger.debug('Determining defaults for IterativeRunner')
        from pyfileconf import PipelineManager

        if not hasattr(self, 'cases'):
            raise ValueError('must set cases before calling get_defaults')
        case = self.cases[0]
        section_path_strs = [
            self._get_full_section_path_str(conf['section_path_str']) for conf in case
        ]
        defaults: Dict[str, Dict[str, Any]] = {}
        for sp_str in section_path_strs:
            pm = PipelineManager.get_manager_by_section_path_str(sp_str)
            sp = SectionPath(sp_str)
            relative_section_path_str = SectionPath(".".join(sp[1:])).path_str
            config = pm.config.get(relative_section_path_str)
            if config is not None:
                defaults[sp_str] = {**config}
        logger.debug(f'Got {defaults} for IterativeRunner.defaults')
        return defaults

    def _fill_case_with_defaults(self, case: Tuple[Dict[str, Any], ...]) -> Tuple[Dict[str, Any], ...]:
        new_confs: List[Dict[str, Any]] = []
        for conf in case:
            sp_str = self._get_full_section_path_str(conf['section_path_str'])
            defaults = self.defaults[sp_str]
            new_conf = {**defaults, **conf}
            new_confs.append(new_conf)
        return tuple(new_confs)

    def _get_full_section_path_str(self, section_path_str: str) -> str:
        if not self.base_section_path_str:
            return section_path_str
        return SectionPath.join(self.base_section_path_str, section_path_str).path_str

    def run(self, collect_results: bool = True) -> IterativeResults:
        """
        :param collect_results: Whether to aggregate and return results, set to False to save memory
            if results are stored in some other way
        :return:
        """
        from pyfileconf.main import PipelineManager
        logger.info(f'Running {self.run_items} with cases')
        all_results = []
        for case in self.cases:
            result = self._run_case(case)
            if collect_results:
                in_out_tup = (case, result)
                all_results.append(in_out_tup)
        logger.debug(f'Finished running {self.run_items} with cases {self.cases}')
        return all_results

    def run_gen(self) -> Iterator[IterativeResult]:
        logger.info(f'Running {self.run_items} with cases')
        for case in self.cases:
            result = self._run_case(case)
            in_out_tup = (case, result)
            yield in_out_tup

    def _run_case(self, case: Tuple[Dict[str, Any], ...]) -> Any:
        case_with_defaults = self._fill_case_with_defaults(case)
        manager.plm.hook.pyfileconf_iter_update_for_case(case=case_with_defaults, runner=self)
        result = self._run()
        self.last_case = case_with_defaults
        return result

    def _run(self) -> Any:
        from pyfileconf.main import PipelineManager

        results = []
        for sp in self.run_items:
            # Look up appropriate manager and run it
            pm = PipelineManager.get_manager_by_section_path_str(sp.path_str)
            relative_section_path_str = SectionPath(".".join(sp[1:])).path_str
            result = pm.run(relative_section_path_str)
            results.append(result)

        if len(results) == 1:
            return results[0]

        return results


def get_config_product(
    config_dicts: Sequence[Dict[str, Any]]
) -> List[Tuple[Dict[str, Any], ...]]:
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


def _get_configs_by_section_path_dict(
    config_dicts: Sequence[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
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
    combined_dicts: Dict[str, List[Dict[str, Any]]] = defaultdict(lambda: [])
    for config_dict in config_dicts:
        conf = deepcopy(config_dict)
        sp = conf["section_path_str"]
        combined_dicts[sp].append(conf)
    return combined_dicts
