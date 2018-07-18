from typing import List
import os

from dero.manager.basemodels.container import Container
from dero.mixins.repr import ReprMixin
from dero.manager.imports.models.statements.container import ImportStatementContainer

StrList = List[str]

scaffolding_error = NotImplementedError('must use DataCollection or PipelineCollection, not base class Collection')

class Collection(Container, ReprMixin):

    #### Scaffolding functions. These should be overridden by collection subclasses ###

    def _set_name_map(self):
        raise scaffolding_error

    def _output_config_files(self):
        raise scaffolding_error

    def _transform_item(self, item):
        """
        Is called on each item when adding items to collection. Should handle whether the item
        is an actual item or another collection. Must return the item or collection.

        If not overridden, will just store items as is.

        Returns: item or Collection

        """
        return item

    ### base functions. These probably do not need to be overridden by collection subclasses ###

    repr_cols = ['name', 'basepath', 'items']

    def __init__(self, basepath: str, items, name: str = None,
                 imports: ImportStatementContainer = None):
        self.basepath = basepath
        self.items = self._transform_items(items)
        self.name = name
        self.imports = imports

    def __getattr__(self, item):
        return self.name_dict[item]

    def __dir__(self):
        return self.name_dict.keys()

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items
        self._set_name_map()  # need to recreate pipeline map when items change

    @classmethod
    def from_dict(cls, dict_: dict, basepath: str, name: str = None,
                  imports: ImportStatementContainer = None):
        items = []
        for section_name, dict_or_list in dict_.items():
            section_basepath = os.path.join(basepath, section_name)
            if isinstance(dict_or_list, dict):
                # Got another pipeline dict. Recursively process
                items.append(
                    cls.from_dict(
                        dict_or_list, basepath=section_basepath, name=section_name, imports=imports
                    )
                )
            elif isinstance(dict_or_list, list):
                # Got a list of functions or pipelines. Create a collection directly from items
                items.append(
                    cls.from_list(
                        dict_or_list, basepath=section_basepath, name=section_name, imports=imports
                    )
                )

        return cls(basepath=basepath, items=items, name=name)

    @classmethod
    def from_list(cls, list_: list, basepath: str, name: str = None,
                  imports: ImportStatementContainer = None):
        items = []
        for dict_or_item in list_:
            if isinstance(dict_or_item, dict):
                items.append(
                    cls.from_dict(
                        dict_or_item, basepath=basepath, name=name, imports=imports
                    )
                )
            else:
                # pipeline or function
                items.append(dict_or_item)

        return cls(basepath=basepath, items=items, name=name, imports=imports)

    def _transform_items(self, items):
        return [self._transform_item(item) for item in items]
