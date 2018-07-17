import ast

from dero.mixins.propertycache import SimplePropertyCacheMixin
from dero.manager.imports.models.statements.interfaces import (
    AnyImportStatement,
    ObjectImportStatement,
    ModuleImportStatement
)
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.io.file.load.parsers.extname import extract_external_name_from_assign_value
from dero.manager.io.func.load.config import FunctionConfigExtractor

class ObjectView(SimplePropertyCacheMixin):

    def __init__(self, obj_ast: ast.AST, import_statement: AnyImportStatement=None,
                 basepath: str=None,
                 section_path_str: str=None):
        self.obj_ast = obj_ast
        self.import_statement = import_statement
        self.basepath = basepath
        self.section_path_str = section_path_str

    def load(self):
        # executes import
        if self.import_statement is not None:
            self.import_statement.execute()

    @property
    def default_config(self):
        return self._try_getattr_else_call_func('_default_config', self._get_default_config)

    @property
    def item(self):
        return self._try_getattr_else_call_func('_item', self._get_real_item)

    @property
    def module(self) -> str:
        return self._try_getattr_else_call_func('_module', self._set_module)

    @property
    def name(self) -> str:
        return self._try_getattr_else_call_func('_name', self._set_name)

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
        self._name = extract_external_name_from_assign_value(self.obj_ast)

    def _get_default_config(self):
        self._default_config = FunctionConfigExtractor(self).extract_config()

    def _get_real_item(self):
        pass