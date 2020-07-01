from typing import Callable, Optional, Union


def pdb_post_mortem_or_passed_debug_fn(
    *args, debug_fn: Union[bool, Callable] = False, **kwargs
) -> None:
    if isinstance(debug_fn, bool):
        if debug_fn:
            post_mortem(*args, **kwargs)
    else:
        post_mortem(*args, debug_fn=debug_fn, **kwargs)


def post_mortem(*args, debug_fn: Optional[Callable] = None, **kwargs) -> None:
    """
    Post-mortem, using a custom debug function if passed

    :param debug_fn:
    :return:
    """
    if debug_fn is None:
        import pdb

        debug_fn = pdb.post_mortem

    debug_fn()
