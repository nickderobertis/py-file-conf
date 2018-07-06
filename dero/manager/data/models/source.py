
import pandas as pd
from functools import partial
import os
import warnings
import datetime
from typing import Callable, TYPE_CHECKING, List

from dero.manager.data.models.type import DataType

if TYPE_CHECKING:
    from dero.manager.data.models.pipeline import DataPipeline

class DataSource:
    _scaffold_items = [
        'name',
        'type',
        'location',
        'loader_func',
        'pipeline',
        'tags'
    ]

    def __init__(self, location: str =None, df: pd.DataFrame =None, pipeline: 'DataPipeline' =None,
                 name: str =None, data_type: str =None, tags: List[str]=None,
                 loader_func: Callable =None, **loader_func_kwargs):
        self._check_inputs(location, df)
        self.location = location
        self.name = name
        self.data_type = data_type
        self.tags = tags # TODO: better handling for tags
        self.loader_func = loader_func
        self.pipeline = pipeline
        self.loader_func_kwargs = loader_func_kwargs
        self._df = df
        self.name_type = f'{name} {self.data_type}'

    def apply_config(self, config) -> None:
        from dero.manager.data.models.config import DataConfig
        config: DataConfig

        for config_attr, config_item in config.items():
            # Skip irrelevant items
            if hasattr(self, config_attr):
                setattr(self, config_attr, config_item)

    @property
    def df(self):
        if self._df is None:
            self._df = self._load()
        return self._df

    @property
    def data_type(self):
        return self._type

    @data_type.setter
    def data_type(self, dtype):
        self._type = DataType(dtype)

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def last_modified(self):
        if self.location is None:
            raise ValueError('no filepath to check for modified time')

        return datetime.datetime.fromtimestamp(os.path.getmtime(self.location))

    def _load(self):
        if not hasattr(self, 'data_loader'):
            self._set_data_loader(data_loader=self.loader_func, pipeline=self.pipeline, **self.loader_func_kwargs)
        return self.data_loader()

    def output(self, **to_csv_kwargs):
        self.df.to_csv(self.location, **to_csv_kwargs)

    def _check_inputs(self, filepath, df):
        pass
        # assert not (filepath is None) and (df is None)

    def _set_data_loader(self, data_loader: Callable =None, pipeline: 'DataPipeline' =None, **loader_func_kwargs):

        if pipeline is not None:
            # if a source in the pipeline to create this data source was modified more recently than this data source
            if pipeline.last_modified > self.last_modified:
                # a prior source used to construct this data source has changed. need to re run pipeline
                recent_source = pipeline.source_last_modified
                warnings.warn(f'''data source {recent_source} was modified at {recent_source.last_modified}.

                this data source {self} was modified at {self.last_modified}.

                to get new changes, will load this data source through pipeline rather than from file.''')

                def run_pipeline_get_result():
                    pipeline.execute()
                    return pipeline.df

                self.data_loader = run_pipeline_get_result
                return
            # otherwise, don't need to worry about pipeline, continue handling

        if data_loader is None:
            # TODO: determine filetype and use proper loader
            self.data_loader = partial(pd.read_csv, self.location, **loader_func_kwargs)
        else:
            self.data_loader = partial(data_loader, self.location, **loader_func_kwargs)

    def __repr__(self):
        return f'<DataSource(name={self.name}, type={self.data_type.name})>'