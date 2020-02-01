from typing import List, cast
import ast
import warnings

from pyfileconf.io.func.load.config import function_args_as_arg_and_annotation_dict
from pyfileconf.io.file.load.parsers.extname import extract_external_name_from_assign_value
from pyfileconf.imports.models.statements.container import ImportStatementContainer, ObjectImportStatement
from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.logic.inspect import _is_str_matching_builtin_type

def extract_import_statements_from_function_args_imports_and_assigns(args: ast.arguments,
                                                                     imports: ImportStatementContainer,
                                                                     assigns: AssignmentStatementContainer,
                                                                     current_module_section_path_str: str,
                                                                     ) -> ImportStatementContainer:
    defaults_dict, annotation_dict = function_args_as_arg_and_annotation_dict(args)

    # Extract external names. These are the root names (not attrs, the base of attrs) for anything that is not builtin
    external_names = _unique_external_names_from_default_dict_and_annotation_dict(defaults_dict, annotation_dict)

    out_imports = ImportStatementContainer([])

    # External names may be either due to assignment or due to imports
    # Handle names due to assignment
    for name in external_names:
        if assigns.contains_varname(name):
            # External name is due to assignment in this module. Create import from this module
            out_imports.append(ObjectImportStatement.from_str(f'from {current_module_section_path_str} import {name}'))

    # Handle names which are imported into this file
    for name in external_names:
        import_or_none = imports.get_import_for_module_or_obj_name(name)
        if import_or_none is not None:
            out_imports.append(import_or_none)

    # Sanity check, did we find all the imports?
    n_external = len(external_names)
    n_imports = len(out_imports)
    if n_external != n_imports:
        warnings.warn(f'had {n_external} external names from function definition, only '
                      f'found {n_imports} imports. May be missing imports')

    return out_imports

def _unique_external_names_from_default_dict_and_annotation_dict(default_dict: dict,
                                                                 annotation_dict: dict) -> List[str]:
    names = _unique_external_names_from_assignment_dict(default_dict)
    names += _unique_external_names_from_annotation_dict(annotation_dict)

    return list(set(names))

def _unique_external_names_from_multiple_assignment_dicts(*assignment_dicts) -> List[str]:
    all_names: List[str] = []
    for assignment_dict in assignment_dicts:
        all_names += _unique_external_names_from_assignment_dict(assignment_dict)
    return list(set(all_names))

def _unique_external_names_from_assignment_dict(assignment_dict: dict) -> List[str]:
    names = [extract_external_name_from_assign_value(value) for key, value in assignment_dict.items()]
    no_none_names: List[str] = [name for name in names if name is not None]
    return list(set(no_none_names))

def _unique_external_names_from_annotation_dict(annotation_dict: dict) -> List[str]:
    type_str_names = _extract_unique_type_str_names_from_annotation_dict(annotation_dict)
    return [type_str for type_str in type_str_names if not _is_str_matching_builtin_type(type_str)]

def _extract_unique_type_str_names_from_annotation_dict(annotation_dict: dict) -> List[str]:
    names = []
    for value in annotation_dict.values():
        names.extend(_extract_str_names_from_ambiguous_annotation(value))

    return list(set(names))

def _extract_str_names_from_ambiguous_annotation(annotation) -> List[str]:
    names = []
    if isinstance(annotation, ast.Name):
        names.append(annotation.id)  # handles most types
    elif isinstance(annotation, ast.Subscript):
        names.extend(_extract_str_names_from_subscript(annotation))
    else:
        raise NotImplementedError(f'no handling for {annotation} of type {type(annotation)}')

    return names

def _extract_str_names_from_subscript(subscript: ast.Subscript) -> List[str]:
    names = []

    # TODO [#26]: remove type ignores once typeshed has better ast support
    #
    # Hitting errors "expr" has no attribute "id" and  "slice" has no attribute "value"

    # e.g.: List[str], gets List portion
    names.append(subscript.value.id) # type: ignore
    if hasattr(subscript.slice.value, 'elts'):  # type: ignore
        # got multiple values, e.g. List[str, bool]
        # in this case, value.slice.value is a Tuple, and Tuple.elts contains the items
        names.extend(_extract_str_names_from_tuple(subscript.slice.value)) # type: ignore
    elif isinstance(subscript.slice.value, ast.Subscript): # type: ignore
        # Recursively call extract from subscript if subscript found within subscript
        # e.g. Optional[List[str]]
        names.extend(_extract_str_names_from_subscript(subscript.slice.value)) # type: ignore
    else:
        # Got a single item, list List[str]
        # gets str portion
        names.append(subscript.slice.value.id)  # type: ignore

    return names

def _extract_str_names_from_tuple(tuple: ast.Tuple) -> List[str]:
    names = []
    for item in tuple.elts:
        names.extend(_extract_str_names_from_ambiguous_annotation(item))
    return names