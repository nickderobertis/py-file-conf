from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.data.models.merge import DataMerge

from pyfileconf.data.logic.merge.summarize import get_summary_of_df
from datacode.display import display_df_dict


def display_merge_summary(merge: 'DataMerge', *summary_args, summary_method: str=None, summary_function: Callable=None,
                          summary_attr: str=None, **summary_method_kwargs):
    # If nothing is passed to use for summary, use df.head()
    if (summary_attr is None) and (summary_function is None) and (summary_method is None):
        summary_method = 'head'

    df_disp_dict = _disp_df_dict_from_merge(
        merge,
        *summary_args,
        summary_method=summary_method,
        summary_function=summary_function,
        summary_attr=summary_attr,
        **summary_method_kwargs
    )

    if summary_attr is not None:
        summary_disp = f'df.{summary_attr}'
    if summary_function is not None:
        summary_disp = f'{summary_function.__name__}(df, *{summary_args}, **{summary_method_kwargs})'
    if summary_method is not None:
        summary_disp = f'df.{summary_method}(*{summary_args}, **{summary_method_kwargs})'

    display_df_dict({
        f'{summary_disp} called on: ' + merge.merge_str: df_disp_dict
    })


def _disp_df_dict_from_merge(merge, *summary_args, summary_method: str=None, summary_function: Callable=None,
                             summary_attr: str=None, **summary_method_kwargs):

    # keys are names of dataframes, values are dataframes themselves
    df_dict = _df_dict_from_merge(merge)

    return {
        name: get_summary_of_df(
            df,
            *summary_args,
            summary_method=summary_method,
            summary_function=summary_function,
            summary_attr=summary_attr,
            **summary_method_kwargs
        ) for name, df in df_dict.items()
    }


def _df_dict_from_merge(merge):
    df_dict = {
        f'Left Dataset: {merge.data_sources[0].name_type}': merge.data_sources[0].df,
        f'Right Dataset: {merge.data_sources[1].name_type}': merge.data_sources[1].df,
        f'Result: {merge.result.name}': merge.result.df
    }

    return df_dict