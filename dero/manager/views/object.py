import ast

from dero.mixins.propertycache import SimplePropertyCacheMixin
from dero.manager.imports.models.statements.interfaces import (
    AnyImportStatement,
    ObjectImportStatement,
    ModuleImportStatement
)
from dero.manager.imports.models.statements.container import ImportStatementContainer

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
    def module_ast(self) -> ast.Module:
        return self._try_getattr_else_call_func('_module_ast', self._set_module_ast)

    @property
    def module_filepath(self) -> str:
        return self._try_getattr_else_call_func('_module_filepath', self._set_module_filepath)

    @classmethod
    def from_ast_and_imports(cls, obj_ast: ast.AST, import_statements: ImportStatementContainer,
                             section_path_str: str=None):
        import_statement = import_statements.get_import_for_ast_obj(obj_ast)

        return cls(
            obj_ast,
            import_statement=import_statement,
            section_path_str=section_path_str
        )

    def _set_module_filepath(self):
        if self.import_statement is None:
            self._module_filepath = None

        if isinstance(self.import_statement, ObjectImportStatement):
            func = lambda: self.import_statement.get_module_filepath(self.section_path_str)
        elif isinstance(self.import_statement, ModuleImportStatement):
            # have already ensured in creating ObjectView that there should be only one module
            # in the module import statement. So just take the first filepath
            func = lambda: self.import_statement.get_module_filepaths(self.section_path_str)[self.import_statement.modules[0]]
        else:
            raise ValueError(f'expected import statement to be ObjectImportStatement or ModuleImportStatement.'
                             f' Got {self.import_statement} of type {type(self.import_statement)}')

        self._module_filepath = func()

    def _set_module_ast(self):
        pass

    def _get_default_config(self):
        pass

    def _get_real_item(self):
        pass