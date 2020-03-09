from typing import List, cast
import ast
import warnings

from pyfileconf.io.func.load.config import function_args_as_arg_and_annotation_dict
from pyfileconf.io.file.load.parsers.extname import extract_unique_external_names_from_assign_value
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
    names = []
    for key, value in assignment_dict.items():
        new_names = extract_unique_external_names_from_assign_value(value)
        names.extend(new_names)
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
    # TODO [#26]: remove type ignores once typeshed has better ast support
    #
    # Hitting errors "expr" has no attribute "id" and  "slice" has no attribute "value"

    names = []
    if isinstance(annotation, ast.Name):
        names.append(annotation.id)  # handles most types
    elif hasattr(annotation, 'elts'):  # type: ignore
        # got multiple values, e.g. List[str, bool]
        # in this case, value.slice.value is a Tuple, and Tuple.elts contains the items
        names.extend(_extract_str_names_from_tuple(annotation)) # type: ignore
    elif isinstance(annotation, ast.Index):
        # e.g. [str]
        # use .value to extract the str part, but then as it can be anything, call recursively on this
        names.extend(_extract_str_names_from_ambiguous_annotation(annotation.value))
    elif isinstance(annotation, ast.Subscript):
        # E.g. Tuple[int]
        names.extend(_extract_str_names_from_subscript(annotation))
    elif isinstance(annotation, ast.Attribute):
        # E.g. pd.DataFrame
        names.append(annotation.value.id)  # type: ignore
    elif isinstance(annotation, ast.Str):
        # E.g. 'DataPipeline' (quoted type declaration where type was imported if TYPE_CHECKING)
        names.append(annotation.s)
    else:
        raise NotImplementedError(f'no handling for {annotation} of type {type(annotation)}')

    return names

def _extract_str_names_from_subscript(subscript: ast.Subscript) -> List[str]:
    names = []

    # for example, List[str]
    outer_ast = subscript.value  # List portion
    inner_ast = subscript.slice  # [str] portion

    names.extend(_extract_str_names_from_ambiguous_annotation(outer_ast))
    names.extend(_extract_str_names_from_ambiguous_annotation(inner_ast))

    return names

def _extract_str_names_from_tuple(tuple: ast.Tuple) -> List[str]:
    names = []
    for item in tuple.elts:
        names.extend(_extract_str_names_from_ambiguous_annotation(item))
    return names