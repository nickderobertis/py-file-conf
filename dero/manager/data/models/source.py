from copy import deepcopy
import pandas as pd
from functools import partial
import os
import warnings
import datetime
from typing import Callable, TYPE_CHECKING, List

from dero.ext_pandas.optimize.load import read_file as read_file_into_df

from dero.manager.data.models.type import DataType
from dero.manager.data.models.astitems import ast_none

if TYPE_CHECKING:
    from dero.manager.data.models.pipeline import DataPipeline

class DataSource:
    _scaffold_dict = {
        'name': ast_none,
        'data_type': ast_none,
        'location': ast_none,
        'loader_func': ast_none,
        'pipeline': ast_none,
        'tags': ast_none
    }

    # TODO: scaffold annotations

    def __init__(self, location: str =None, df: pd.DataFrame =None, pipeline: 'DataPipeline' =None,
                 name: str =None, data_type: str =None, tags: List[str]=None,
                 loader_func: Callable =None, loader_func_kwargs: dict=None):

        if loader_func_kwargs is None:
            loader_func_kwargs = {}

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
            # No location. Setting last modified time as a long time ago, so will trigger pipeline instead
            return datetime.datetime(1899, 1, 1)

        return datetime.datetime.fromtimestamp(os.path.getmtime(self.location))

    def _load(self):
        self._touch_pipeline()
        if not hasattr(self, 'data_loader'):
            self._set_data_loader(data_loader=self.loader_func, pipeline=self.pipeline, **self.loader_func_kwargs)
        return self.data_loader()

    def output(self, **to_csv_kwargs):
        self.df.to_csv(self.location, **to_csv_kwargs)

    def _check_inputs(self, filepath, df):
        pass
        # assert not (filepath is None) and (df is None)

    def _set_data_loader(self, data_loader: Callable =None, pipeline: 'DataPipeline' =None, **loader_func_kwargs):
        run_pipeline = False
        if pipeline is not None:
            # if a source in the pipeline to create this data source was modified more recently than this data source
            # note: if there is no location, will always enter the next block, as last modified time will set
            # to a long time ago
            if pipeline.last_modified > self.last_modified:
                # a prior source used to construct this data source has changed. need to re run pipeline
                recent_source = pipeline.source_last_modified
                warnings.warn(f'''data source {recent_source} was modified at {recent_source.last_modified}.

                this data source {self} was modified at {self.last_modified}.

                to get new changes, will load this data source through pipeline rather than from file.''')

                run_pipeline = True
            # otherwise, don't need to worry about pipeline, continue handling

        if self.location is None:
            # no location or pipeline, so accessing df will return empty dataframe
            loader = pd.DataFrame
        else:
            if data_loader is None:
                # TODO: determine filetype and use proper loader
                loader = partial(read_file_into_df, self.location, **loader_func_kwargs)
            else:
                loader = partial(data_loader, self.location, **loader_func_kwargs)

        # If necessary, run pipeline before loading
        # Still necessary to use loader as may be transforming the data
        if run_pipeline:
            def run_pipeline_then_load(pipeline):
                pipeline.execute() # outputs to file
                return loader()
            self.data_loader = partial(run_pipeline_then_load, self.pipeline)
        else:
            self.data_loader = loader


    def _touch_pipeline(self):
        """
        Pipeline may be passed using dero.manager.Selector, in which case it is
        a dero.manager.selector.models.itemview.ItemView object. _set_data_loader accesses a property of
        the pipeline before it's configured, and so won't work correctly. By accessing the .item proprty of the ItemView,
        we get the original item back
        Returns:

        """
        from dero.manager.selector.models.itemview import _is_item_view

        if _is_item_view(self.pipeline):
            self.pipeline = self.pipeline.item

    def copy(self):
        return deepcopy(self)

    def __repr__(self):
        return f'<DataSource(name={self.name}, type={self.data_type.name})>'