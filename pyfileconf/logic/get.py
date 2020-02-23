from typing import List
from pyfileconf.sectionpath.sectionpath import SectionPath

accepted_name_attrs = ['name', '__name__']
output_accepted_name_attrs = ['output_name'] + accepted_name_attrs


def _get_from_nested_obj_by_section_path(obj, section_path: SectionPath, prevent_property_access: bool = False):
    """

    :param obj:
    :param section_path:
    :param prevent_property_access: Whether to prevent accessing properties. This is used in selector as the
        selector is working with the unconfigured objects for lookup, and the unconfigured objects' properties
        could cause errors or other side effects
    :return:
    """
    # Goes into nested sections, until it pulls the final section or pipeline
    for section in section_path:

        # When preventing property access, checks if next accessed attribute is actually a property
        try:
            if prevent_property_access and isinstance(getattr(type(obj), section), property):
                # Next section would access a property, which could lead to unintended side-effects
                # Therefore, return an object which is not a collection, function, or specific class object,
                # as this will signal to calling functions that the full section path is not a stored object

                # the returned value is totally arbitrary so long as it is not a collection,
                # function, or specific class object
                return 5
        except AttributeError:
            # If there is no property to look up under this name, then just continue as normal.
            # Not exactly sure why this was needed since the next code will raise the same error, but
            # for some reason it won't work without this try/except block
            pass

        obj = getattr(obj, section)

    return obj


def _get_public_name_or_special_name(obj, accept_output_names=True) -> str:
    name_attrs = _get_name_attrs(accept_output=accept_output_names)
    for name_var in name_attrs:
        if hasattr(obj, name_var):
            return getattr(obj, name_var)

    raise ValueError(f'could not get .name or .__name__ from {obj} of type {type(obj)}')

def _has_public_name_or_special_name(obj, accept_output_names=True) -> bool:
    name_attrs = _get_name_attrs(accept_output=accept_output_names)
    for name_var in name_attrs:
        if hasattr(obj, name_var):
            return True

    return False

def _get_name_attrs(accept_output: bool=True) -> List[str]:
    if accept_output:
        return output_accepted_name_attrs
    else:
        return accepted_name_attrs