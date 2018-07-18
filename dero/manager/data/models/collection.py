from typing import List, Union
import os

from dero.manager.basemodels.collection import Collection
from dero.manager.data.models.source import DataSource
from dero.manager.data.logic.convert import convert_list_of_strs_or_data_sources_to_data_sources
from dero.manager.logic.get import _get_public_name_or_special_name
from dero.manager.data.models.config import DataConfig
from dero.manager.imports.models.statements.container import ImportStatementContainer


SourceOrCollection = Union[DataSource, 'DataCollection']

class DataCollection(Collection):

    def __init__(self, basepath: str, items, name: str = None,
                 imports: ImportStatementContainer = None):
        items = convert_list_of_strs_or_data_sources_to_data_sources(items)
        super().__init__(basepath, items, name=name, imports=imports)

    def _set_name_map(self) -> None:
        source_map = {}
        for source_or_collection in self:
            source_or_collection: SourceOrCollection
            source_name = _get_public_name_or_special_name(source_or_collection)
            source_map[source_name] = source_or_collection
        self.name_dict = source_map

    def _output_config_files(self) -> None:
        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        [self._output_config_file(item) for item in self]

    def _output_config_file(self, item: SourceOrCollection) -> None:
        if isinstance(item, DataCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with DataSource
        item_name = _get_public_name_or_special_name(item) + '.py'
        item_filepath = os.path.join(self.basepath, item_name)

        if os.path.exists(item_filepath):
            # if config file already exists, load confguration from file, use to update file defaults
            existing_config = DataConfig.from_file(item_filepath)
            existing_imports = existing_config._file.interface.imports
            # also use to update DataSource object in memory
            item.apply_config(existing_config)
        else:
            existing_imports = None

        item_config = DataConfig.from_source(item, imports=existing_imports)
        item_config.to_file(item_filepath)
