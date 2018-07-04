
import pandas as pd
from functools import partial
import os
import warnings
import datetime
from typing import Callable, TYPE_CHECKING

from dero.manager.data.models.type import DataType

if TYPE_CHECKING:
    from dero.manager.data.models.pipeline import DataPipeline





class DataSource:

    def __init__(self, filepath: str =None, df: pd.DataFrame =None, pipeline: 'DataPipeline' =None,
                 name: str =None, type: str =None, loader_func: Callable =None, **loader_func_kwargs):
        self._check_inputs(filepath, df)
        self.filepath = filepath
        self.name = name
        self.type = DataType(type)
        self._loader_cache = (loader_func, pipeline, loader_func_kwargs)
        self._df = df
        self.name_type = f'{name} {self.type}'

    @property
    def df(self):
        if self._df is None:
            self._df = self._load()
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def last_modified(self):
        if self.filepath is None:
            raise ValueError('no filepath to check for modified time')

        return datetime.datetime.fromtimestamp(os.path.getmtime(self.filepath))

    def _load(self):
        if not hasattr(self, 'data_loader'):
            loader_func = self._loader_cache[0]
            pipeline = self._loader_cache[1]
            loader_func_kwargs = self._loader_cache[2]
            self._set_data_loader(data_loader=loader_func, pipeline=pipeline, **loader_func_kwargs)
        return self.data_loader()

    def output(self, **to_csv_kwargs):
        self.df.to_csv(self.filepath, **to_csv_kwargs)

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
            self.data_loader = partial(pd.read_csv, self.filepath, **loader_func_kwargs)
        else:
            self.data_loader = partial(data_loader, self.filepath, **loader_func_kwargs)

    def __repr__(self):
        return f'<DataSource(name={self.name}, type={self.type.name})>'