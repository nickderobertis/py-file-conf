from typing import Callable
from copy import deepcopy

from dero.manager.data.logic.merge.display import display_merge_summary
from dero.manager.data.models.source import DataSource
from dero.manager.data.logic.merge import left_merge_df
from dero.data.summarize import describe_df

class MergeOptions:

    def __init__(self, *merge_function_args, outpath=None, merge_function=left_merge_df, **merge_function_kwargs):
        self.args = merge_function_args
        self.outpath = outpath
        self.merge_function = merge_function
        self.merge_function_kwargs = merge_function_kwargs

    def __repr__(self):
        return f'<DataMerge(args={self.args}, merge_function={self.merge_function.__name__}, ' \
               f'kwargs={self.merge_function_kwargs})>'

    def copy(self):
        return deepcopy(self)

    def update(self, **kwargs):
        self.merge_function_kwargs.update(**kwargs)


class DataMerge:

    def __init__(self, data_sources: [DataSource], merge_options: MergeOptions):
        self.data_sources = data_sources
        self.merge_options = merge_options
        self._merged_name = None
        self._merged_type = None
        self._merged_str = None
        self._set_result(merge_options.outpath)

    def merge(self):
        print(f'Running merge function {self.merge_str}')
        self.result.df = self.merge_options.merge_function(
            self.data_sources[0].df, self.data_sources[1].df,
            *self.merge_options.args,
            **self.merge_options.merge_function_kwargs
        )
        print(f"""
        {self.data_sources[0].name_type} obs: {len(self.data_sources[0].df)}
        {self.data_sources[1].name_type} obs: {len(self.data_sources[1].df)}
        Merged obs: {len(self.result.df)}
        """)

    def summary(self, *summary_args, summary_method: str=None, summary_function: Callable=None,
                             summary_attr: str=None, **summary_method_kwargs):
        display_merge_summary(
            self,
            *summary_args,
            summary_method=summary_method,
            summary_function=summary_function,
            summary_attr=summary_attr,
            **summary_method_kwargs
        )

    def describe(self):
        display_merge_summary(
            self,
            summary_function=describe_df,
            disp=False # don't display from describe_df as will display from display_merge_summary
        )

    def _set_result(self, outpath=None):
        self.result = DataSource(outpath, name=self.merged_name, data_type=self.merged_type)

    @property
    def merged_name(self):
        if self._merged_name is None:
            self._merged_name = self.data_sources[0].name + ' & ' + self.data_sources[1].name
        return self._merged_name

    @property
    def merged_type(self):
        if self._merged_type is None:
            self._merged_type = self.data_sources[0].data_type + ' & ' + self.data_sources[1].data_type
        return self._merged_type

    @property
    def merge_str(self):
        if self._merged_str is None:
            self._merged_str = f'''
            {self.merge_options.merge_function.__name__}(
                {self.data_sources[0].name_type},
                {self.data_sources[1].name_type},
                *{self.merge_options.args},
                **{self.merge_options.merge_function_kwargs}
            )
            '''
        return self._merged_str

    def __repr__(self):
        return f'<DataMerge(left={self.data_sources[0]}, right={self.data_sources[1]})>'


class LastMergeFinishedException(Exception):
    pass


