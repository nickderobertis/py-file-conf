
from dero.manager.selector.logic import get_dict_of_pipeline_manager_names_and_instances_from_globals
from dero.manager.logic.get import _get_from_nested_obj_by_section_path
from dero.manager.sectionpath.sectionpath import SectionPath

class Selector:

    def __init__(self):
        self._attach_to_pipeline_manager()

    def __getattr__(self, item):
        return self._managers[item]

    def __call__(self, item):
        section_path = SectionPath(item)
        return _get_from_nested_obj_by_section_path(self, section_path)

    def _attach_to_pipeline_manager(self):
        self._managers = get_dict_of_pipeline_manager_names_and_instances_from_globals()