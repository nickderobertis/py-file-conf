import ast

from dero.mixins.propertycache import SimplePropertyCacheMixin
from dero.manager.imports.models.statements.interfaces import AnyImportStatement
from dero.manager.imports.models.statements.container import ImportStatementContainer

class ObjectView(SimplePropertyCacheMixin):

    def __init__(self, obj_ast: ast.AST, import_statement: AnyImportStatement=None,
                 section_path_str: str=None):
        self.obj_ast = obj_ast
        self.import_statement = import_statement
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

    @classmethod
    def from_ast_and_imports(cls, obj_ast: ast.AST, import_statements: ImportStatementContainer,
                             section_path_str: str=None):
        import_statement = import_statements.get_import_for_ast_obj(obj_ast)

        return cls(
            obj_ast,
            import_statement=import_statement,
            section_path_str=section_path_str
        )

    def _get_default_config(self):
        pass

    def _get_real_item(self):
        pass