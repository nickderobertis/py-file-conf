from collections import defaultdict
from typing import Dict, Set, Optional, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from pyfileconf.main import PipelineManager
    from pyfileconf.selector.models.itemview import ItemView
    from pyfileconf.sectionpath.sectionpath import SectionPath


class PyFileConfContext:
    config_dependencies: Dict[str, Set['SectionPath']]
    active_managers: Dict[str, 'PipelineManager']
    force_update_dependencies: Dict[str, Set['SectionPath']]
    file_is_currently_being_loaded: bool
    currently_running_section_path_str: Optional[str]

    def __init__(self, config_dependencies: Optional[Dict[str, Set['SectionPath']]] = None,
                 active_managers: Optional[Dict[str, 'PipelineManager']] = None,
                 force_update_dependencies: Optional[Dict[str, Set['SectionPath']]] = None,
                 file_is_currently_being_loaded: bool = False,
                 currently_running_section_path_str: Optional[str] = None):
        if config_dependencies is None:
            config_dependencies = defaultdict(lambda: set())
        if active_managers is None:
            active_managers = {}
        if force_update_dependencies is None:
            force_update_dependencies = defaultdict(lambda: set())

        self.config_dependencies = config_dependencies
        self.active_managers = active_managers
        self.force_update_dependencies = force_update_dependencies
        self.file_is_currently_being_loaded = file_is_currently_being_loaded
        self.currently_running_section_path_str = currently_running_section_path_str

    def reset(self):
        self.config_dependencies = defaultdict(lambda: set())
        self.active_managers = {}
        self.force_update_dependencies = defaultdict(lambda: set())
        self.file_is_currently_being_loaded = False
        self.currently_running_section_path_str = None

    def add_config_dependency(self, dependent: Union[str, 'ItemView', 'SectionPath'],
                              depends_on: Union[str, 'ItemView', 'SectionPath'], force_update: bool = False):
        from pyfileconf.sectionpath.sectionpath import SectionPath
        dependent_section_path = SectionPath.from_ambiguous(dependent)
        depends_on_section_path_str = SectionPath.from_ambiguous(depends_on).path_str
        self.config_dependencies[depends_on_section_path_str].add(dependent_section_path)
        if force_update:
            self.force_update_dependencies[depends_on_section_path_str].add(dependent_section_path)

    def add_config_dependency_for_currently_running_item_if_exists(self, depends_on: Union[str, 'ItemView', 'SectionPath'],
                                                                   force_update: bool = False):
        if self.currently_running_section_path_str is not None:
            self.add_config_dependency(
                self.currently_running_section_path_str, depends_on, force_update=force_update
            )

    def add_config_dependency_if_file_is_currently_being_loaded(
        self,
        dependent: Union[str, 'ItemView', 'SectionPath'],
        depends_on: Union[str, 'ItemView', 'SectionPath'],
        force_update: bool = False
    ):
        if self.file_is_currently_being_loaded:
            self.add_config_dependency(dependent, depends_on, force_update=force_update)


context = PyFileConfContext()
