from copy import deepcopy
from typing import Union, cast, Any
import os

from pyfileconf.basemodels.collection import Collection
from pyfileconf.data.logic.convert import convert_to_empty_obj_if_necessary
from pyfileconf.logic.get import _get_public_name_or_special_name
from pyfileconf.data.models.config import SpecificClassConfig


ObjOrCollection = Union[Any, 'SpecificClassCollection']

class SpecificClassCollection(Collection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.klass is None:
            raise ValueError('must pass class for SpecificClassCollection')

    def _set_name_map(self) -> None:
        obj_map = {}
        for obj_or_collection in self:
            obj_or_collection = cast(ObjOrCollection, obj_or_collection)
            obj_name = _get_public_name_or_special_name(obj_or_collection)
            obj_map[obj_name] = obj_or_collection
        self.name_dict = obj_map

    def _transform_item(self, item):
        """
        Is called on each item when adding items to collection. Should handle whether the item
        is an actual item or another collection. Must return the item or collection.

        If not overridden, will just store items as is.

        Returns: item or Collection

        """
        return convert_to_empty_obj_if_necessary(item, self.klass)

    def _output_config_files(self) -> None:
        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        for item in self:
            self._output_config_file(item)

    def _output_config_file(self, item: ObjOrCollection) -> None:
        if isinstance(item, SpecificClassCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with object itself
        item_name = _get_public_name_or_special_name(item)
        item_filepath = os.path.join(self.basepath, item_name + '.py')

        class_config = dict(
            klass=self.klass,
            always_import_strs=self.always_import_strs,
            always_assign_strs=self.always_assign_strs
        )

        if os.path.exists(item_filepath):
            file_existed = True
            # if config file already exists, load confguration from file, use to update file defaults
            existing_config = SpecificClassConfig.from_file(
                item_filepath,
                name=item_name,
                **class_config
            )
            existing_imports = existing_config._file.interface.imports
            # Here using the ast config, for the purpose of writing to file
            file_config_item = deepcopy(item)
            apply_config(file_config_item, existing_config)
            # also use to update DataSource object in memory. Here use the actual objects instead of ast
            apply_config(item, existing_config.active_config_dict)
        else:
            file_existed = False
            existing_imports = None
            file_config_item = item

        item_config = SpecificClassConfig.from_obj(file_config_item, imports=existing_imports,
                                                   file_path=item_filepath, **class_config)
        item_config.to_file(item_filepath)

        if not file_existed:
            # If this was a new output, we now need to load again to get the object representation
            # instead of just the ast representation
            existing_config = SpecificClassConfig.from_file(item_filepath, item_name, **class_config)
            apply_config(item, existing_config.active_config_dict)


def apply_config(obj: Any, config: 'SpecificClassConfig') -> None:
    for config_attr, config_item in config.items():
        # Skip irrelevant items
        if hasattr(obj, config_attr):
            setattr(obj, config_attr, config_item)