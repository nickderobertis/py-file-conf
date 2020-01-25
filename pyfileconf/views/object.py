import ast

from mixins.propertycache import SimplePropertyCacheMixin
from pyfileconf.imports.models.statements.interfaces import (
    AnyImportStatement,
    ObjectImportStatement,
    ModuleImportStatement
)
from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.io.file.load.parsers.extname import extract_external_name_from_assign_value
from pyfileconf.io.file.load.parsers.kwargs import extract_keywords_from_ast_by_name
from pyfileconf.io.func.load.config import FunctionConfigExtractor
from mixins.repr import ReprMixin

class ObjectView(SimplePropertyCacheMixin, ReprMixin):
    repr_cols = ['name', 'obj_ast', 'section_path_str']

    def __init__(self, obj_ast: ast.AST, import_statement: AnyImportStatement=None,
                 section_path_str: str=None):
        self.obj_ast = obj_ast
        self.import_statement = import_statement
        self.section_path_str = section_path_str

    def load(self):
        # executes import
        if self.import_statement is not None:
            self._item = _execute_import_get_obj_from_result(self.import_statement, self.name)

        return self._item

    @property
    def default_config(self):
        return self._try_getattr_else_call_func('_default_config', self._get_default_config)

    @property
    def item(self):
        return self._try_getattr_else_call_func('_item', self.load)

    @property
    def module(self) -> str:
        return self._try_getattr_else_call_func('_module', self._set_module)

    @property
    def name(self) -> str:
        return self._try_getattr_else_call_func('_name', self._set_name)

    @property
    def output_name(self) -> str:
        try:
            return self._output_name
        except AttributeError:
            return self.name

    @classmethod
    def from_ast_and_imports(cls, obj_ast: ast.AST, import_statements: ImportStatementContainer,
                             section_path_str: str=None):
        import_statement = import_statements.get_import_for_ast_obj(obj_ast)

        return cls(
            obj_ast,
            import_statement=import_statement,
            section_path_str=section_path_str
        )

    def _set_module(self):
        if self.import_statement is None:
            self._module = None

        if isinstance(self.import_statement, ObjectImportStatement):
            self._module = self.import_statement.module
        elif isinstance(self.import_statement, ModuleImportStatement):
            # have already ensured in creating ObjectView that there should be only one module
            # in the module import statement. So just take the first module
            self._module = self.import_statement.modules[0]
        else:
            raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                             f' Got {self.import_statement} of type {type(self.import_statement)}')

    def _set_name(self):
        name = extract_external_name_from_assign_value(self.obj_ast)
        if name == 'DataPipeline':
            # DataPipeline may be passed in pipeline dict. Then need to get name from DataPipeline constructor
            ast_name = extract_keywords_from_ast_by_name(self.obj_ast, 'name')['name']
            self._output_name = ast_name.s
        self._name = name

    def _get_default_config(self):
        self._default_config = FunctionConfigExtractor(self).extract_config(self.name)


def _execute_import_get_obj_from_result(import_statement: AnyImportStatement, obj_name: str):
    # Should be just a single module or object, can take first of either.
    result = import_statement.execute()[0]

    if isinstance(import_statement, ObjectImportStatement):
        # Result is the object itself
        return result
    elif isinstance(import_statement, ModuleImportStatement):
        # Result is the module. Get the object from the module
        return getattr(result, obj_name)
    else:
        raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                         f' Got {import_statement} of type {type(import_statement)}')