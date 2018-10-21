
from dero.mixins.repr import ReprMixin
from dero.mixins.attrequals import EqOnAttrsMixin
from dero.manager.selector.models.selector import Selector
from dero.manager.exceptions.pipelinemanager import PipelineManagerNotLoadedException
from dero.manager.sectionpath.sectionpath import SectionPath
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

            # check whether this is an item attribute or a typo
            manager_name = SectionPath(full_section_path_str)[0]
            if manager_name in self.selector._managers:  # if manager is loaded
                # Even though manager is loaded, cannot find item. it is likely a typo.
                raise ItemNotFoundException(f'could not find item {full_section_path_str}')
            else:
                raise PipelineManagerNotLoadedException('create pipeline manager instance before using selectors')


        return getattr(actual_item, item)

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
        cls = self.__class__
        result = cls.__new__(cls)
        memodict[id(self)] = result
        deepcopy_skip_items = ['selector']
        deepcopy_dict = {key: value for key, value in self.__dict__.items() if key not in deepcopy_skip_items}
        shallow_copy_dict = {key: value for key, value in self.__dict__.items() if key in deepcopy_skip_items}
        for k, v in deepcopy_dict.items():
            setattr(result, k, deepcopy(v, memodict))
        result.__dict__.update(shallow_copy_dict)
        return result

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

class ItemNotFoundException(Exception):
    pass

def _is_item_view(obj) -> bool:
    is_item_view = getattr(obj, '_is_item_view', False)
    return is_item_view