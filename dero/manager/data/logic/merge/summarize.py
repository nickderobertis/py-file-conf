from typing import Callable


def get_summary_of_df(df, *summary_args, summary_method: str=None, summary_function: Callable=None,
                      summary_attr: str=None, **summary_method_kwargs):
    try:
        if summary_method is not None:
            return getattr(df, summary_method)(*summary_args, **summary_method_kwargs)
        if summary_function is not None:
            return summary_function(df, *summary_args, **summary_method_kwargs)
        if summary_attr is not None:
            return getattr(df, summary_attr)
    except Exception as e:
        # keep going, but save exception as result
        return e