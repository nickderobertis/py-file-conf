from typing import Callable, List, Union, Tuple
from copy import deepcopy
import pandas as pd
from functools import partial

from dero.manager.data.logic.merge.display import display_merge_summary
from dero.manager.data.models.source import DataSource
from dero.manager.data.logic.merge import left_merge_df
from dero.data.summarize import describe_df

StrList = List[str]
StrListOrNone = Union[None, StrList]
TwoDfTuple = Tuple[pd.DataFrame, pd.DataFrame]

class MergeOptions:

    def __init__(self, *merge_function_args, outpath=None, merge_function=left_merge_df,
                 left_df_keep_cols: StrListOrNone=None, right_df_keep_cols: StrListOrNone=None,
                 left_df_pre_process_func: Callable=None, right_df_pre_process_func: Callable=None,
                 left_df_pre_process_kwargs: dict=None, right_df_pre_process_kwargs: dict=None,
                 **merge_function_kwargs):
        """

        passed args to merge func will be (
            left_df_pre_process_func(left_df, **left_df_pre_process_kwargs)[left_df_keep_cols],
            right_df_pre_process_func(right_df, **right_df_pre_process_kwargs)[right_df_keep_cols],
            *merge_function_kwargs,
            **merge_function_kwargs
        )

        if left_df_keep_cols is None, will instead pass left_df_pre_process_func(left_df, **left_df_pre_process_kwargs).
        If right_df_keep_cols is None, will instead pass right_df_pre_process_func(right_df, **right_df_pre_process_kwargs).
        If left_df_pre_process_func is None, will instead pass left_df or left_df[left_df_keep_cols] depending
            on whether left_df_keep_cols was passed. Similar behavior for right.

        Args:
            *merge_function_args:
            outpath:
            merge_function:
            left_df_keep_cols:
            right_df_keep_cols:
            **merge_function_kwargs:
        """

        if left_df_pre_process_kwargs == None:
            left_df_pre_process_kwargs = {}

        if right_df_pre_process_kwargs == None:
            right_df_pre_process_kwargs = {}

        if left_df_pre_process_func == None:
            left_df_pre_process_func = lambda x: x

        if right_df_pre_process_func == None:
            right_df_pre_process_func = lambda x: x

        self.args = merge_function_args
        self.outpath = outpath
        self.merge_function = merge_function
        self.merge_function_kwargs = merge_function_kwargs
        self.left_df_keep_cols = left_df_keep_cols
        self.right_df_keep_cols = right_df_keep_cols
        self.left_df_pre_process_func = partial(left_df_pre_process_func, **left_df_pre_process_kwargs)
        self.right_df_pre_process_func = partial(right_df_pre_process_func, **right_df_pre_process_kwargs)


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
        left_df, right_df = self._get_merge_dfs()
        self.result.df = self.merge_options.merge_function(
            left_df, right_df,
            *self.merge_options.args,
            **self.merge_options.merge_function_kwargs
        )
        print(f"""
        {self.data_sources[0].name_type} obs: {len(left_df)}
        {self.data_sources[1].name_type} obs: {len(right_df)}
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

    def _get_merge_dfs(self) -> TwoDfTuple:
        left_df = self.data_sources[0].df
        right_df = self.data_sources[1].df

        # Handle pre process funcs
        if self.merge_options.left_df_pre_process_func is not None:
            left_df = self.merge_options.left_df_pre_process_func(left_df)
        if self.merge_options.right_df_pre_process_func is not None:
            right_df = self.merge_options.right_df_pre_process_func(right_df)

        # Handle selecting variables on processed df
        if self.merge_options.left_df_keep_cols is not None:
            left_df = left_df[self.merge_options.left_df_keep_cols]
        if self.merge_options.right_df_keep_cols is not None:
            right_df = right_df[self.merge_options.right_df_keep_cols]

        return left_df, right_df

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


