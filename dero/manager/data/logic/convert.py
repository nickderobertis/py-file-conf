from typing import Union

from dero.manager.data.models.source import DataSource

StrOrDataSource = Union[str, DataSource]

def convert_to_data_source_if_necessary(item: StrOrDataSource) -> DataSource:
    from dero.manager.data.models.collection import DataCollection
    if isinstance(item, (DataSource, DataCollection)):
        return item

    return DataSource(name=item)