import ast
from typing import TYPE_CHECKING, Tuple, Optional, cast

from pyfileconf.exceptions.imports import NoImportStatementException

if TYPE_CHECKING:
    from pyfileconf.views.object import ObjectView
from importlib.util import resolve_name

from pyfileconf.imports.models.statements.interfaces import (
    ObjectImportStatement,
    ModuleImportStatement,
    AnyImportStatement
)

from pyfileconf.io.file.load.parsers.funcdef import extract_function_definition_or_class_init_from_ast_by_name
from pyfileconf.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader
from pyfileconf.imports.models.statements.container import ImportStatementContainer

ArgumentsAndImports = Tuple[ast.arguments, ImportStatementContainer]

class FunctionArgsExtractor:

    def __init__(self, object_view: 'ObjectView'):
        self.object_view = object_view

    def extract_args(self) -> ArgumentsAndImports:
        return extract_function_args_and_arg_imports_from_import(
            self.object_view.name,
            self.object_view.import_statement,
            self.object_view.section_path_str
        )


def extract_function_args_and_arg_imports_from_import(function_name: str, imp: Optional[AnyImportStatement],
                                                      import_section_path_str: Optional[str] = None) -> ArgumentsAndImports:
    from pyfileconf.io.func.load.extractimp import extract_import_statements_from_function_args_imports_and_assigns

    if imp is None:
        raise NoImportStatementException('no import passed to extract function and imports')

    filepath = get_module_filepath_from_import(
        imp,
        import_section_path_str
    )

    if function_name in imp.renames.new_names:
        # If was renamed in the import,
        # Get original name from rename statement
        function_name = imp.renames.reverse_name_map[function_name]

    loader = ImportAssignmentLazyLoader(filepath)

    # TODO [#44]: handle relative nested imports such as from .this import that
    #
    # This code keeps importing and checking whether the name is defined in the file. If not,
    # it follows the next import. This doesn't properly work if one of those followed imports
    # is a relative import such as `from .this import that`. Add test to show this and
    # also fix it.

    ast_function_def = extract_function_definition_or_class_init_from_ast_by_name(
        loader.ast,
        function_name
    )

    if ast_function_def is not None:
        # Found function definition in this import
        # TODO [#12]: handle other class methods - also update extract_function_definition function
        if ast_function_def.name == '__init__':
            # Got class init
            del ast_function_def.args.args[0]  # delete first arg (self)
        function_arg_imports = extract_import_statements_from_function_args_imports_and_assigns(
            ast_function_def.args,
            loader.imports,
            loader.assigns,
            imp.module
        )
        return ast_function_def.args, function_arg_imports

    # Else, this function must have been imported into this file as well.
    # Must find the matching import, the extract args from that import
    next_level_import = loader.imports.get_import_for_module_or_obj_name(function_name)
    if next_level_import is None:
        raise ValueError(f'not able to find function definition for {function_name}. Could not '
                         f'find in definitions or in imports')

    if import_section_path_str is not None:
        next_module = next_level_import.module
        new_section_path = resolve_name(next_module, import_section_path_str) if next_module.startswith('.') else next_module
    else:
        new_section_path = None

    return extract_function_args_and_arg_imports_from_import(
        function_name,
        imp=next_level_import,
        import_section_path_str=new_section_path
    )


def get_module_filepath_from_import(imp: Optional[AnyImportStatement], import_section_path_str: Optional[str]):
    if imp is None:
        return None

    # TODO [#30]: figure out why mypy won't pick up that imp is not None in get_module_filepath_from_import
    #
    # Then type ignores can be removed
    if isinstance(imp, ObjectImportStatement):
        func = lambda: imp.get_module_filepath(import_section_path_str)
    elif isinstance(imp, ModuleImportStatement):
        # have already ensured in creating ObjectView that there should be only one module
        # in the module import statement. So just take the first filepath
        func = lambda: imp.get_module_filepaths(import_section_path_str)[imp.modules[0]]  # type: ignore
    else:
        raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                         f' Got {imp} of type {type(imp)}')

    return func()