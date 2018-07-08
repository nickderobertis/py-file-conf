import builtins

def _is_builtin(value: any) -> bool:
    if value is None:
        return True # None won't return True from the following check

    builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
    return type(value) in builtin_types