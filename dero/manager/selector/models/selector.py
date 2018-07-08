from typing import Callable
import warnings

from dero.manager.selector.logic.get.main import get_dict_of_any_defined_pipeline_manager_names_and_instances
from dero.manager.logic.get import _get_from_nested_obj_by_section_path
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.logic.load import get_pipeline_dict_and_data_dict_from_filepaths
from dero.manager.selector.logic.get.frommanager import get_pipeline_dict_path_and_data_dict_path_from_manager
from dero.manager.pipelines.models.collection import PipelineCollection
from dero.manager.basemodels.pipeline import Pipeline
from dero.manager.data.models.collection import DataCollection, DataSource

class Selector:

    def __init__(self):
        self._attach_to_pipeline_manager()
        self._load_structure()

    def __contains__(self, item):
        if not isinstance(item, (str, SectionPath)):
            warnings.warn('check for if non-str object in Selector will always return False')
            return False

        collection_obj, relative_section_path = self._get_collection_obj_and_relative_section_path_from_structure(item)

        if relative_section_path is None:
            # got only the root data path, e.g. project.sources. Return the collection object itself
            return collection_obj

        # Only should return True if we find an ItemView
        # Three possible cases here.
        # Accessing a non-existent attr, should catch KeyError then return False
        # Accessing an existing item, should be a collection, source, or function instance, return True
        # Accessing an existing attribute of an existing item, should not be an ItemView instance, return False
        try:
            result = _get_from_nested_obj_by_section_path(collection_obj, relative_section_path)
        except KeyError:
            return False

        # TODO: converting all functions to pipelines would make this check safer
        item_types = (DataSource, DataCollection, Pipeline, PipelineCollection, Callable)
        if isinstance(result, item_types):
            return True

        return False


    def __getattr__(self, item):
        from dero.manager.selector.models.itemview import ItemView
        return ItemView(item, self)

    def __call__(self, item):
        from dero.manager.selector.models.itemview import ItemView
        return ItemView(item, self)

    def _get_collection_obj_and_relative_section_path_from_structure(self, section_path_str: str):
        # Handle accessing correct collection object.
        section_path = SectionPath(section_path_str)
        manager_name = section_path[0]
        if section_path[1] == 'sources':
            # got a data path
            if len(section_path) == 2:
                # got only the root data path, e.g. project.sources
                # return the collection object itself
                return self._structure[manager_name]['data'], None
            collection_name = 'data'
            section_path_begin_index = 2
        else:
            collection_name = 'funcs'
            section_path_begin_index = 1

        relative_section_path = SectionPath('.'.join(section_path[section_path_begin_index:]))
        collection_obj = self._structure[manager_name][collection_name]

        return collection_obj, relative_section_path

    def get_type(self, section_path_str: str):
        collection_obj, relative_section_path = self._get_collection_obj_and_relative_section_path_from_structure(
            section_path_str
        )

        if relative_section_path is None:
            # got only the root data path, e.g. project.sources. Return the collection object itself
            return collection_obj

        # TODO: nicer error than KeyError for typo
        result = _get_from_nested_obj_by_section_path(collection_obj, relative_section_path)

        return type(result)

    def _get_real_item(self, item):
        section_path = SectionPath(item)
        manager_name = section_path[0]
        manager = self._managers[manager_name]
        relative_section_path = SectionPath('.'.join(section_path[1:]))
        return _get_from_nested_obj_by_section_path(manager, relative_section_path)

    def _attach_to_pipeline_manager(self):
        self._managers = get_dict_of_any_defined_pipeline_manager_names_and_instances()

    def _load_structure(self):
        out_dict = {}
        for manager_name, manager in self._managers.items():
            pipeline_dict_path, data_dict_path = get_pipeline_dict_path_and_data_dict_path_from_manager(manager)
            pipeline_dict, data_dict = get_pipeline_dict_and_data_dict_from_filepaths(pipeline_dict_path, data_dict_path)
            manager_dict = {
                'funcs': PipelineCollection.from_dict(pipeline_dict, manager.basepath),
                'data': DataCollection.from_dict(data_dict, manager.basepath)
            }
            out_dict[manager_name] = manager_dict
        self._structure = out_dict




