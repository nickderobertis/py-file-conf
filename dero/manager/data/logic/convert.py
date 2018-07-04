from typing import List, Union

from dero.manager.data.models.source import DataSource

StrOrDataSource = Union[str, DataSource]

def convert_list_of_strs_or_data_sources_to_data_sources(list_ : List[StrOrDataSource]) -> List[DataSource]:
    return [_convert_to_data_source_if_necessary(item) for item in list_]


def _convert_to_data_source_if_necessary(item: StrOrDataSource) -> DataSource:
    if isinstance(item, DataSource):
        return item

    return DataSource(name=item)