from typing import List, Optional
from mixins.attrequals import EqOnAttrsMixin
from pyfileconf.mixins.orderpref import OrderPreferenceMixin

class ImportStatement(EqOnAttrsMixin, OrderPreferenceMixin):
    rename_attr: Optional[str] = None

    ### Scaffolding methods

    def execute(self):
        # execute import statement
        raise NotImplementedError('use ModuleImportStatement or ObjectImportStatement, not base ImportStatement')

    #### Common class methods and properties

    @property
    def _renamed(self):
        if self.rename_attr is None:
            raise ValueError(f'must set rename_attr in class {self.__class__.__name__}')
        rename_items: List = getattr(self, self.rename_attr)

        if self.renames is None:
            return rename_items # no saved renames, just return original attrs

        renamed_items = []
        for item in rename_items:
            if item in self.renames:
                renamed_items.append(str(self.renames[item]))
            else:
                renamed_items.append(item)

        return renamed_items
