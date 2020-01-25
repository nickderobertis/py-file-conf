from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from pyfileconf.main import PipelineManager

from pyfileconf.exceptions.pipelinemanager import PipelineManagerNotLoadedException
from pyfileconf.sectionpath.sectionpath import SectionPath


def handle_pipeline_manager_not_loaded_or_typo(full_section_path_str: str, managers: List['PipelineManager']):
    manager_name = SectionPath(full_section_path_str)[0]
    if manager_name in managers:  # if manager is loaded
        # Even though manager is loaded, cannot find item. it is likely a typo.
        raise ItemNotFoundException(f'could not find item {full_section_path_str}')
    else:
        raise PipelineManagerNotLoadedException('create pipeline manager instance before using selectors')


def handle_known_typo_at_end_of_section_path_str(full_section_path_str: str):
    parts = full_section_path_str.split('.')
    raise ItemNotFoundException(f'could not find item {parts[-1]} of collection {".".join(parts[1:-1])} '
                                f'in pipeline manager {parts[0]}\n\ncheck spelling in {full_section_path_str}')


def handle_known_typo_after_pipeline_manager_name(full_section_path_str: str):
    parts = full_section_path_str.split('.')
    raise ItemNotFoundException(f'check spelling on first attribute after pipeline manager {parts[0]}')


class ItemNotFoundException(Exception):
    pass
