import sys
from importlib._bootstrap import _find_spec
from importlib.util import resolve_name
from importlib.machinery import ModuleSpec


def get_filepath_from_module_str(module_str: str, location_section_path_str: str=None):
    spec: ModuleSpec = find_spec(module_str, package=location_section_path_str)
    if not spec.has_location:
        raise ValueError(f'could not find location of module {module_str}, package {location_section_path_str}')

    return spec.origin

def find_spec(name, package=None) -> ModuleSpec:
    """Return the spec for the specified module.

    Note: this is a modification of importlib.util.find_spec which does not
    import parent packages. It instead recursively searches through the parents.

    First, sys.modules is checked to see if the module was already imported. If
    so, then sys.modules[name].__spec__ is returned. If that happens to be
    set to None, then ValueError is raised. If the module is not in
    sys.modules, then sys.meta_path is searched for a suitable spec with the
    value of 'path' given to the finders. None is returned if no spec could
    be found.

    If the name is for submodule (contains a dot), find_spec is called on the
    parent module to determine the submodule_search_locations.

    The name and package arguments work the same as importlib.import_module().
    In other words, relative module names (with leading dots) work.

    """
    fullname = resolve_name(name, package) if name.startswith('.') else name
    if fullname not in sys.modules:
        parent_name = fullname.rpartition('.')[0]
        if parent_name:
            # Use builtins.__import__() in case someone replaced it.
            parent = find_spec(parent_name, package=package)
            return _find_spec(fullname, parent.submodule_search_locations)
        else:
            return _find_spec(fullname, None)
    else:
        module = sys.modules[fullname]
        if module is None:
            return None
        try:
            spec = module.__spec__
        except AttributeError:
            raise ValueError('{}.__spec__ is not set'.format(name)) from None
        else:
            if spec is None:
                raise ValueError('{}.__spec__ is None'.format(name))
            return spec