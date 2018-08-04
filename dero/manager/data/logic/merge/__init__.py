import pandas as pd

def _how_merge_df(df: pd.DataFrame, other_df: pd.DataFrame, ids, how='left'):
    return df.merge(other_df, on=ids, how=how)

def outer_merge_df(df: pd.DataFrame, other_df: pd.DataFrame, ids):
    return _how_merge_df(df, other_df, ids, how='outer')

def left_merge_df(df: pd.DataFrame, other_df: pd.DataFrame, ids):
    return _how_merge_df(df, other_df, ids, how='left')

def right_merge_df(df: pd.DataFrame, other_df: pd.DataFrame, ids):
    return _how_merge_df(df, other_df, ids, how='right')