import inspect
from functools import partial
from typing import cast, List, Type, Dict, Tuple, Any

from pyfileconf.data.models.collection import SpecificClassCollection
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.selector.logic.exc.typo import (
    handle_pipeline_manager_not_loaded_or_typo,
    handle_known_typo_at_end_of_section_path_str,
    handle_known_typo_after_pipeline_manager_name
)
from pyfileconf.selector.models.selector import Selector
from pyfileconf.exceptions.pipelinemanager import PipelineManagerNotLoadedException
from copy import deepcopy


class ItemView:
    """
    Class for representing a pipeline manager unit (function, pipeline, data source) without needing
    that unit to be loaded into pipeline manager. Allows using selector in config files and in app,
    by delaying looking up the item until an attribute/method is accessed or item is called.
    """

    def __init__(self, section_path_str: str, selector: Selector):
        self.section_path_str = section_path_str
        self._section_path_str = section_path_str  # for compatibility with real items which have this attribute added
        self.selector = selector
        self._is_item_view = True

    def __getattr__(self, item):
        from pyfileconf.main import PipelineManager
        full_section_path_str = self.section_path_str + '.' + item
        if full_section_path_str in self.selector:
            # This is an item, return an item view for it
            return ItemView(full_section_path_str, self.selector)

        # Not an item.
        # Must be either an attribute of an item, or a typo. Actually look up the item now

        try:
            actual_item = self.item
        except PipelineManagerNotLoadedException:
            # Dealing with typos is difficult because if this is a typo and we are reaching here,
            # if PipelineManager.load() has not been run yet, we can't know the attributes of the items,

            # check whether this is an item attribute or a typo, and raise error if needed
            return handle_pipeline_manager_not_loaded_or_typo(full_section_path_str, self.selector._managers)

        # TODO [#18]: refactor item view lookup errors
        #
        #  So that there is a better way of catching a known typo than python throwing a RecursionError

        except RecursionError:
            # We are landing here when there is a typo in after the pipeline manager selection of a longer
            # section path, e.g if "this" was portfolio manager name: s.this.tpyo.would.cause.this
            return handle_known_typo_after_pipeline_manager_name(full_section_path_str)

        try:
            result = getattr(actual_item, item)
        except (KeyError, AttributeError) as e:
            ### TEMP - having issues with _is_selector
            raise e
            ### END TEMP
            return handle_known_typo_at_end_of_section_path_str(full_section_path_str)

        # Got attribute of actual item
        # If this happened while running another item, add to dependencies
        self._add_to_config_dependencies_if_necessary()

        return result

    def __setattr__(self, key: str, value):
        # Set these items on ItemView itself
        item_view_set_attrs = [
            'section_path_str',
            'selector',
            '_is_item_view',
            '_section_path_str',
        ]
        if key in item_view_set_attrs:
            super().__setattr__(key, value)
        else:
            # Set any others on the original object via updating PipelineManager config
            self.selector._set_attr_for_item(self.section_path_str, key, value)

    def __dir__(self):
        exposed_properties = [
            'type',
            'item'
        ]
        collection_attrs = self.selector._get_dir_for_section_path(self.section_path_str)
        return exposed_properties + collection_attrs

    def __call__(self, *args, **kwargs):
        from pyfileconf import PipelineManager

        # When calling, assume user always wants the real item
        actual_item = self.selector._get_real_item(self.section_path_str)
        # If this happened while running another item, add to dependencies
        self._add_to_config_dependencies_if_necessary()

        # Determine whether this object is from a specific class collection
        manager = PipelineManager.get_manager_by_section_path_str(self.section_path_str)
        collection_name = SectionPath(self.section_path_str)[1]
        try:
            manager._registrar_dict[collection_name]
            specific_class = True
        except KeyError:
            specific_class = False

        # Handle depending on the type of item
        if isinstance(actual_item, partial):
            # Got a function in the general registrar
            func = actual_item
        elif specific_class and isinstance(actual_item, self._specific_classes):
            # Got specific registrar class
            # Need to look up the execute attribute and apply section path str
            actual_item._section_path_str = self.section_path_str
            collection = self._specific_class_collection_map[type(actual_item)]
            execute_attr = collection.execute_attr
            func = getattr(actual_item, execute_attr)
        else:
            cannot_parse_error = ValueError(f'could not parse actual item, expected partial, '
                                            f'specific class, or method of specific class. '
                                            f'Got {actual_item} of type {type(actual_item)}')
            orig_item: Any = None
            try:
                orig_item = actual_item.__self__
                is_bound_method = True
            except AttributeError:
                is_bound_method = False

            if is_bound_method:
                if not isinstance(orig_item, self._specific_classes):
                    # Is bound method, but not for one of defined specific classes
                    raise cannot_parse_error

                # Got specific class method
                # Add section path to original item and then set method to be called
                orig_item_sp = SectionPath.from_section_str_list(SectionPath(self.section_path_str)[:-1])
                orig_item_sp_str = orig_item_sp.path_str
                orig_item._section_path_str = orig_item_sp_str
                func = actual_item
            else:
                if inspect.isclass(actual_item):
                    raise cannot_parse_error
                # Got a class object in the general registrar
                actual_item._section_path_str = self.section_path_str
                # Simply return it
                return actual_item

        result = func(*args, **kwargs)
        return result

    def __deepcopy__(self, memodict={}):
        return deepcopy(self.item, memodict)

    def __eq__(self, other):
        equal_attrs = ['section_path_str']

        for equal_attr in equal_attrs:
            if not hasattr(other, equal_attr): # other object doesn't have this property, must not be equal
                return False
            if getattr(self, equal_attr) != getattr(other, equal_attr):
                return False

        # passed all checks, must be equal
        return True

    def __hash__(self):
        return hash(self.section_path_str)

    def __repr__(self):
        repr_cols = ['section_path_str']

        repr_col_strs = [f'{col}={getattr(self, col, None).__repr__()}' for col in repr_cols]
        repr_col_str = f'({", ".join(repr_col_strs)})'

        return f'<{type(self).__name__}{repr_col_str}>'

    @property
    def __class__(self) -> Type:
        return self.type

    @__class__.setter
    def __class__(self, value):
        # Setting class has no effect, still use type of underlying item
        pass

    @property
    def type(self) -> Type:
        return self.selector.get_type(self.section_path_str)

    @property
    def item(self):
        return self.selector._get_real_item(self.section_path_str)

    def _add_to_config_dependencies_if_necessary(self):
        from pyfileconf.context import context
        context.add_config_dependency_for_currently_running_item_if_exists(self.section_path_str, force_update=True)

    @property
    def _specific_class_collection_map(self) -> Dict[Type, SpecificClassCollection]:
        class_collection_map: Dict[Type, SpecificClassCollection] = {}
        for manager_name, manager_dict in self.selector._structure.items():
            for collection_name, collection in manager_dict.items():
                if collection_name == '_general':
                    continue
                class_collection_map[collection.klass] = collection
        return class_collection_map

    @property
    def _specific_classes(self) -> Tuple[Type, ...]:
        return tuple(self._specific_class_collection_map.keys())

    @classmethod
    def from_section_path_str(cls, section_path_str: str) -> 'ItemView':
        """
        Constructs an ItemView from a section path str

        :param section_path_str: Must be the full section path
            str containing the pipeline manager name
        :return:
        """
        s = Selector()
        sp = SectionPath(section_path_str)
        if len(sp) < 2:
            raise ValueError(f'got invalid section path str {section_path_str}')
        iv = cast(ItemView, s)
        for part in sp:
            iv = getattr(iv, part)
        return iv


def is_item_view(obj: Any) -> bool:
    """
    Determine whether an object is an :class:`ItemView`.

    When using the Selector, objects are proxied by ItemViews
    until an attribute is accessed. The ItemView is set up
    so that it will work nearly completely like the
    original object, including isinstance checks. In fact
    isinstance(item, ItemView) will always return False
    on an ItemView as the class appears to be the original
    class. This function is the preferred way to check
    whether an object is an ItemView.

    :param obj: An object which may or may not be an ItemView
    :return: Whether the object is an ItemView
    """
    this_is_item_view = getattr(obj, '_is_item_view', False)
    if this_is_item_view:
        obj = cast(ItemView, obj)
    return this_is_item_view
