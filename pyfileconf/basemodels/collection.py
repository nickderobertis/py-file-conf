from typing import List, Optional, Sequence, Type
import os

from pyfileconf.basemodels.container import Container
from mixins.repr import ReprMixin
from pyfileconf.imports.models.statements.container import ImportStatementContainer

StrList = List[str]

scaffolding_error = NotImplementedError('must use SpecificClassCollection or PipelineCollection, not base class Collection')

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
                 imports: ImportStatementContainer = None, always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                 key_attr: str = 'name'):
        self.basepath = basepath
        self.imports = imports
        self.name = name

        self.always_import_strs = always_import_strs
        self.always_assign_strs = always_assign_strs
        self.key_attr = key_attr
        self.klass = klass
        self.items = self._transform_items(items)
        self._set_name_map()

    def __getattr__(self, item):
        try:
            return self.name_dict[item]
        except KeyError:
            raise AttributeError(f'{item}')

    def __dir__(self):
        return self.name_dict.keys()

    @property  # type: ignore
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items
        self._set_name_map()  # need to recreate pipeline map when items change

    @classmethod
    def from_dict(cls, dict_: dict, basepath: str, name: str = None,
                  imports: ImportStatementContainer = None, always_import_strs: Optional[Sequence[str]] = None,
                  always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                  key_attr: str = 'name'):
        items = []
        for section_name, dict_or_list in dict_.items():
            section_basepath = os.path.join(basepath, section_name)
            if isinstance(dict_or_list, dict):
                # Got another pipeline dict. Recursively process
                items.append(
                    cls.from_dict(
                        dict_or_list, basepath=section_basepath, name=section_name, imports=imports,
                        always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
                        key_attr=key_attr
                    )
                )
            elif isinstance(dict_or_list, list):
                # Got a list of functions or pipelines. Create a collection directly from items
                items.append(
                    cls.from_list(
                        dict_or_list, basepath=section_basepath, name=section_name, imports=imports,
                        always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
                        key_attr=key_attr
                    )
                )

        return cls(
            basepath=basepath, items=items, name=name,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr
        )

    @classmethod
    def from_list(cls, list_: list, basepath: str, name: str = None,
                  imports: ImportStatementContainer = None, always_import_strs: Optional[Sequence[str]] = None,
                  always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                  key_attr: str = 'name'):
        items = []
        for dict_or_item in list_:
            if isinstance(dict_or_item, dict):
                # Dict within list means that there is no name for the dict. Instead just access the keys
                # of the dict by their names.
                for section_name, dict_list_or_item in dict_or_item.items():
                    section_basepath = os.path.join(basepath, section_name)
                    if isinstance(dict_list_or_item, dict):
                        collection = cls.from_dict(
                            dict_list_or_item, basepath=section_basepath, name=section_name, imports=imports,
                            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
                            key_attr=key_attr
                        )
                    elif isinstance(dict_list_or_item, list):
                        collection = cls.from_list(
                            dict_list_or_item, basepath=section_basepath, name=section_name, imports=imports,
                            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
                            key_attr=key_attr
                        )
                    else:
                        collection = dict_list_or_item
                    items.append(collection)
            else:
                # pipeline or function
                items.append(dict_or_item)

        return cls(
            basepath=basepath, items=items, name=name, imports=imports,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr
        )

    def to_nested_dict(self):
        return to_nested_dict(self)

    def _transform_items(self, items):
        return [self._transform_item(item) for item in items]


def to_nested_dict(collection: Collection):
    out_dict = {}
    for item in collection:
        if isinstance(item, Collection):
            nested = to_nested_dict(item)
            out_dict[item.name] = nested
        else:
            out_dict[item.name] = item
    return out_dict