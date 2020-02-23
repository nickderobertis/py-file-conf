from typing import Callable, List, Any
import warnings

from pyfileconf.logic.get import _get_from_nested_obj_by_section_path
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.selector.logic.get.frommanager import get_pipeline_dict_path_and_specific_class_config_dicts_from_manager
from pyfileconf.pipelines.models.collection import PipelineCollection
from pyfileconf.basemodels.pipeline import Pipeline
from pyfileconf.data.models.collection import SpecificClassCollection
from pyfileconf.views.object import ObjectView

class Selector:

    def __init__(self):
        self._attach_to_pipeline_manager()
        self._load_structure()
        self._is_selector = True

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
        # Accessing a non-existent attr, should catch AttributeError then return False
        # Accessing an existing item, should be a collection, source, or function instance, return True
        # Accessing an existing attribute of an existing item, should not be an ItemView instance, return False
        try:
            result = _get_from_nested_obj_by_section_path(
                collection_obj,
                relative_section_path,
                prevent_property_access=True
            )
        except AttributeError:
            return False

        # TODO [#19]: convert all functions to pipelines
        #
        # it would make this check safer

        item_types = (SpecificClassCollection, Pipeline, PipelineCollection, Callable, ObjectView, collection_obj.klass)
        if isinstance(result, item_types):
            return True

        return False


    def __getattr__(self, item):
        from pyfileconf.selector.models.itemview import ItemView
        return ItemView(item, self)

    def __call__(self, item):
        from pyfileconf.selector.models.itemview import ItemView
        return ItemView(item, self)

    def __dir__(self):
        exposed_methods = [
            'get_type'
        ]

        managers = list(self._managers.keys())

        return exposed_methods + managers

    def _get_dir_for_section_path(self, section_path_str: str) -> List[str]:
        collection_obj, relative_section_path = self._get_collection_obj_and_relative_section_path_from_structure(
            section_path_str
        )
        if relative_section_path is None:
            # got only the root data path, e.g. project.sources. Return the collection object itself
            return dir(collection_obj)

        result_obj = _get_from_nested_obj_by_section_path(collection_obj, relative_section_path)

        return dir(result_obj)

    def _get_collection_obj_and_relative_section_path_from_structure(self, section_path_str: str):
        # Handle accessing correct collection object.
        section_path = SectionPath(section_path_str)
        manager_name = section_path[0]

        if len(section_path) == 1:
            # Got only the manager, e.g. project
            # return only the manager itself
            return self._managers[manager_name], None

        if section_path[1] in self._managers[manager_name].specific_class_names:
            # got a specific class path
            if len(section_path) == 2:
                # got only the root data path, e.g. project.sources
                # return the collection object itself
                return self._structure[manager_name][section_path[1]], None
            collection_name = section_path[1]
            section_path_begin_index = 2
        else:
            collection_name = '_general'
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

        # TODO [#20]: nicer error than KeyError for typo
        result = _get_from_nested_obj_by_section_path(collection_obj, relative_section_path)

        return type(result)

    def _get_real_item(self, item):
        section_path = SectionPath(item)
        manager_name = section_path[0]
        manager = self._managers[manager_name]
        relative_section_path = SectionPath('.'.join(section_path[1:]))
        return _get_from_nested_obj_by_section_path(manager, relative_section_path)

    def _set_attr_for_item(self, item: str, attr: str, value: Any):
        section_path = SectionPath(item)
        manager_name = section_path[0]
        manager = self._managers[manager_name]
        relative_section_path_str = '.'.join(section_path[1:])
        manager.config.update(
            {attr: value},
            section_path_str=relative_section_path_str
        )

    def _attach_to_pipeline_manager(self):
        from pyfileconf.main import PipelineManager
        self._managers = PipelineManager._active_managers

    def _load_structure(self):
        from pyfileconf.main import create_collections
        from pyfileconf import PipelineManager
        out_dict = {}
        manager: PipelineManager
        for manager_name, manager in self._managers.items():
            pipeline_dict_path, specific_class_name_config_dict = get_pipeline_dict_path_and_specific_class_config_dicts_from_manager(manager)
            collections, general_collection = create_collections(
                specific_class_name_config_dict,
                manager.default_config_path,
                manager.folder,
                pipeline_dict_path,
            )
            manager_dict = {
                '_general': general_collection,
            }
            for collection in collections:
                manager_dict.update({
                    collection.name: collection
                })
            out_dict[manager_name] = manager_dict
        self._structure = out_dict




def _is_selector(obj) -> bool:
    is_selector = getattr(obj, '_is_selector', False)
    return is_selector