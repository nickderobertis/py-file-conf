
# these modules are causing issues. Skip them when scanning for objects in modules
skip_modules = [
    'six.moves',  # causes error ModuleNotFoundError: No module named '_gdbm'
]