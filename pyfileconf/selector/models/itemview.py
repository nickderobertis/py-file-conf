from typing import cast

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
        self.selector = selector
        self._is_item_view = True

    def __getattr__(self, item):
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
            return getattr(actual_item, item)
        except (KeyError, AttributeError) as e:
            ### TEMP - having issues with _is_selector
            raise e
            ### END TEMP
            return handle_known_typo_at_end_of_section_path_str(full_section_path_str)

    def __setattr__(self, key: str, value):
        # Set these items on ItemView itself
        item_view_set_attrs = [
            'section_path_str',
            'selector',
            '_is_item_view',
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
        # When calling, assume user always wants the real item
        actual_item = self.selector._get_real_item(self.section_path_str)
        return actual_item(*args, **kwargs)

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

    def __repr__(self):
        repr_cols = ['section_path_str']

        repr_col_strs = [f'{col}={getattr(self, col, None).__repr__()}' for col in repr_cols]
        repr_col_str = f'({", ".join(repr_col_strs)})'

        return f'<{type(self).__name__}{repr_col_str}>'

    @property
    def type(self):
        return self.selector.get_type(self.section_path_str)

    @property
    def item(self):
        return self.selector._get_real_item(self.section_path_str)


def _is_item_view(obj) -> bool:
    is_item_view = getattr(obj, '_is_item_view', False)
    if is_item_view:
        obj = cast(ItemView, obj)
    return is_item_view
