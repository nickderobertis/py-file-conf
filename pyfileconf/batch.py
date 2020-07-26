import itertools
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict, Any, Tuple, Sequence, Optional, Iterator, Iterable

from pyfileconf.plugin import manager
from pyfileconf.runner.models.interfaces import RunnerArgs, IterativeResults, IterativeResult
from pyfileconf.sectionpath.sectionpath import SectionPath


class BatchUpdater:
    """
    Class that enables config changes across multiple pipeline managers

    Update one or multiple registered functions/sections by their full
    section paths, regardless of in which manager they reside
    """
    updates: Iterable[Dict[str, Any]]
    strip_manager_from_iv: bool

    def __init__(
        self,
        base_section_path_str: Optional[str] = None,
        strip_manager_from_iv: bool = False,
    ):
        """
        :param base_section_path_str: section path str to put at beginning of all passed section paths
        :param strip_manager_from_iv: whether to remove manager name from any incoming item views
        """
        self.base_section_path_str = base_section_path_str
        self.strip_manager_from_iv = strip_manager_from_iv

    def update(self, updates: Iterable[Dict[str, Any]]) -> None:
        """
        :param updates: list of kwarg dictionaries which would normally be provided to .update_batch
        :return:
        """
        from pyfileconf.main import PipelineManager

        updates_lol = manager.plm.hook.pyfileconf_pre_update_batch(
            pm=self, updates=updates
        )

        all_updates = itertools.chain(*updates_lol)
        for update in all_updates:
            sp = SectionPath.from_ambiguous(
                update['section_path_str'],
                base_section_path_str=self.base_section_path_str,
                strip_manager_from_iv=self.strip_manager_from_iv
            )
            pm = PipelineManager.get_manager_by_section_path_str(sp.path_str)
            relative_section_path_str = SectionPath(".".join(sp[1:])).path_str
            new_update = {**update, 'section_path_str': relative_section_path_str}
            pm._update(**new_update)

        manager.plm.hook.pyfileconf_post_update_batch(
            pm=self, updates=updates
        )

    def reset(self, section_path_strs: Iterable[str]):
        from pyfileconf.main import PipelineManager

        for sp_str in section_path_strs:
            sp = SectionPath.from_ambiguous(
                sp_str,
                base_section_path_str=self.base_section_path_str,
                strip_manager_from_iv=self.strip_manager_from_iv
            )
            pm = PipelineManager.get_manager_by_section_path_str(sp.path_str)
            relative_section_path_str = SectionPath(".".join(sp[1:])).path_str
            pm.reset(relative_section_path_str)