from IPython.display import display, HTML
import pandas as pd

def display_df_dict(df_dict):
    # df_dict may either be one level deep or two levels deep.
    # if two levels deep, then first level organizes which table it is,
    # and the second level is panels
    for df_name in df_dict:
        df_or_dict = df_dict[df_name]
        # Handle the case where it is two levels deep
        if isinstance(df_or_dict, dict):
            display(HTML(f'<h2>{df_name}</h2>'))
            display_df_dict(df_or_dict)
        elif isinstance(df_or_dict, pd.DataFrame):
            _display_df(df_or_dict, df_name)
        else:
            raise ValueError('Must pass a dict containing dataframes')

def _display_df(df, df_name):
    display(HTML(f'<h3>{df_name}</h3>'))
    display(df)