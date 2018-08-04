from IPython.display import display, HTML
import pandas as pd
from typing import Sequence

def display_df_dict(df_dict):
    # df_dict may either be one level deep or two levels deep.
    # if two levels deep, then first level organizes which table it is,
    # and the second level is panels
    for df_name in df_dict:
        df_or_dict_or_dfs = df_dict[df_name]
        # Handle the case where it is two levels deep
        if isinstance(df_or_dict_or_dfs, dict):
            display(_html_from_str(df_name))
            display_df_dict(df_or_dict_or_dfs)
        elif isinstance(df_or_dict_or_dfs, (list, tuple)):
            display_dfs(df_or_dict_or_dfs, df_name)
        else:
            _display_df(df_or_dict_or_dfs, df_name)

def display_dfs(df_list: Sequence[pd.DataFrame], title: str=None) -> None:

    if title is not None:
        display(_html_from_str(title, tag_type='h3'))

    display(*df_list)


def _display_df(df, df_name):
    display(_html_from_str(df_name, tag_type='h3'))
    display(df)

def _html_from_str(str_: str, tag_type='h2') -> HTML:
    return HTML(f'<{tag_type}>{str_}</{tag_type}>')