import ast
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.views.object import ObjectView
from importlib.util import resolve_name

from dero.manager.imports.models.statements.interfaces import (
    ObjectImportStatement,
    ModuleImportStatement,
    AnyImportStatement
)

from dero.manager.io.file.load.parsers.funcdef import extract_function_definition_from_ast_by_name
from dero.manager.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader

class FunctionArgsExtractor:

    def __init__(self, object_view: 'ObjectView'):
        self.object_view = object_view

    def extract_args(self) -> List[ast.arg]:
        return extract_function_args_from_import(
            self.object_view.name,
            self.object_view.import_statement,
            self.object_view.section_path_str
        )


def extract_function_args_from_import(function_name: str, imp: AnyImportStatement,
                                      import_section_path_str: str=None) -> List[ast.arg]:

    filepath = get_module_filepath_from_import(
        imp,
        import_section_path_str
    )

    if function_name in imp.renames.new_names:
        # If was renamed in the import,
        # Get original name from rename statement
        function_name = imp.renames.reverse_name_map[function_name]

    loader = ImportAssignmentLazyLoader(filepath)

    ast_function_def = extract_function_definition_from_ast_by_name(
        loader.ast,
        function_name
    )

    if ast_function_def is not None:
        # Found function definition in this import
        return ast_function_def.args

    # Else, this function must have been imported into this file as well.
    # Must find the matching import, the extract args from that import
    next_level_import = loader.imports.get_import_for_module_or_obj_name(function_name)
    if next_level_import is None:
        raise ValueError(f'not able to find function definition for {function_name}. Could not '
                         f'find in definitions or in imports')

    if import_section_path_str is not None:
        # Deal with searching in the correct location
        if isinstance(next_level_import, ObjectImportStatement):
            next_module = next_level_import.module
        elif isinstance(next_level_import, ModuleImportStatement):
            # above function creating next_level_import ensures only one module
            next_module = next_level_import.modules[0]
        else:
            raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                             f' Got {next_level_import} of type {type(next_level_import)}')
        new_section_path = resolve_name(next_module, import_section_path_str) if next_module.startswith('.') else next_module
    else:
        new_section_path = None

    return extract_function_args_from_import(
        function_name,
        imp=next_level_import,
        import_section_path_str=new_section_path
    )




def get_module_filepath_from_import(imp: AnyImportStatement, import_section_path_str: str):
    if imp is None:
        return None

    if isinstance(imp, ObjectImportStatement):
        func = lambda: imp.get_module_filepath(import_section_path_str)
    elif isinstance(imp, ModuleImportStatement):
        # have already ensured in creating ObjectView that there should be only one module
        # in the module import statement. So just take the first filepath
        func = lambda: imp.get_module_filepaths(import_section_path_str)[imp.modules[0]]
    else:
        raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                         f' Got {imp} of type {type(imp)}')

    return func()