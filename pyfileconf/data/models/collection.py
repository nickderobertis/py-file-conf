from typing import Union
import os

from pyfileconf.basemodels.collection import Collection
from pyfileconf.data.models.source import DataSource
from pyfileconf.data.logic.convert import convert_to_data_source_if_necessary
from pyfileconf.logic.get import _get_public_name_or_special_name
from pyfileconf.data.models.config import DataConfig


SourceOrCollection = Union[DataSource, 'DataCollection']

class DataCollection(Collection):

    def _set_name_map(self) -> None:
        source_map = {}
        for source_or_collection in self:
            source_or_collection: SourceOrCollection
            source_name = _get_public_name_or_special_name(source_or_collection)
            source_map[source_name] = source_or_collection
        self.name_dict = source_map

    def _transform_item(self, item):
        """
        Is called on each item when adding items to collection. Should handle whether the item
        is an actual item or another collection. Must return the item or collection.

        If not overridden, will just store items as is.

        Returns: item or Collection

        """
        return convert_to_data_source_if_necessary(item)

    def _output_config_files(self) -> None:
        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        [self._output_config_file(item) for item in self]

    def _output_config_file(self, item: SourceOrCollection) -> None:
        if isinstance(item, DataCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with DataSource
        item_name = _get_public_name_or_special_name(item)
        item_filepath = os.path.join(self.basepath, item_name + '.py')

        if os.path.exists(item_filepath):
            file_existed = True
            # if config file already exists, load confguration from file, use to update file defaults
            existing_config = DataConfig.from_file(item_filepath, item_name)
            existing_imports = existing_config._file.interface.imports
            # Here using the ast config, for the purpose of writing to file
            file_config_item = item.copy()
            file_config_item.apply_config(existing_config)
            # also use to update DataSource object in memory. Here use the actual objects instead of ast
            item.apply_config(existing_config.active_config_dict)
        else:
            file_existed = False
            existing_imports = None
            file_config_item = item

        item_config = DataConfig.from_source(file_config_item, imports=existing_imports)
        item_config.to_file(item_filepath)

        if not file_existed:
            # If this was a new output, we now need to load again to get the object representation
            # instead of just the ast representation
            existing_config = DataConfig.from_file(item_filepath, item_name)
            item.apply_config(existing_config.active_config_dict)