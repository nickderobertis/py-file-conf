
from dero.mixins.repr import ReprMixin
from dero.mixins.attrequals import EqOnAttrsMixin
from dero.manager.selector.models.selector import Selector

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

    def __getattr__(self, item):
        full_section_path_str = self.section_path_str + '.' + item
        if full_section_path_str in self.selector:
            # This is an item, return an item view for it
            return ItemView(full_section_path_str, self.selector)

        # Not an item.
        # Must be either an attribute of an item, or a typo. Actually look up the item now
        actual_item = self.selector._get_real_item(self.section_path_str)
        return getattr(actual_item, item)

    def __call__(self, *args, **kwargs):
        # When calling, assume user always wants the real item
        actual_item = self.selector._get_real_item(self.section_path_str)
        return actual_item(*args, **kwargs)

