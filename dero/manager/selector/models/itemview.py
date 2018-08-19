
from dero.mixins.repr import ReprMixin
from dero.mixins.attrequals import EqOnAttrsMixin
from dero.manager.selector.models.selector import Selector
from dero.manager.exceptions.pipelinemanager import PipelineManagerNotLoadedException
from copy import deepcopy


class ItemView(ReprMixin, EqOnAttrsMixin):
    """
    Class for representing a pipeline manager unit (function, pipeline, data source) without needing
    that unit to be loaded into pipeline manager. Allows using selector in config files and in app,
    by delaying looking up the item until an attribute/method is accessed or item is called.
    """
    repr_cols = ['section_path_str']
    equal_attrs = ['section_path_str']

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
            # so there is no certain way to check whether this is an item attribute or a typo
            # TODO: check if manager is loaded, if so, then do a proper check. otherwise return a general error
            # TODO: saying that it could be either manager not being loaded or a typo and display part of the path not found
            raise PipelineManagerNotLoadedException


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

    @property
    def type(self):
        return self.selector.get_type(self.section_path_str)

    @property
    def item(self):
        return self.selector._get_real_item(self.section_path_str)
