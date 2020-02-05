from typing import List, Optional
import ast

from pyfileconf.basemodels.container import Container
from mixins.repr import ReprMixin

from pyfileconf.exceptions.imports import NoImportMatchingNameException
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.imports.models.statements.module import ModuleImportStatement
from pyfileconf.imports.models.statements.interfaces import (
    AnyImportStatementOrComment,
    Comment,
    ImportOrNone
)
from pyfileconf.imports.models.statements.rename import RenameStatementCollection
from pyfileconf.io.file.load.parsers.extname import extract_external_name_from_assign_value

class ImportStatementContainer(Container, ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: List[AnyImportStatementOrComment]):
        self.items = items

    def __contains__(self, item: AnyImportStatementOrComment):
        for imp_or_comment in self:
            if item == imp_or_comment:
                return True

            if not isinstance(item, (ObjectImportStatement, ModuleImportStatement)) or \
               not isinstance(imp_or_comment, (ObjectImportStatement, ModuleImportStatement)):
                # only further handling is for actual imports, skip comments, etc.
                continue

            # handle where item is a subset of an import statement in the collection.

            # first handle where it's a module import statement
            # e.g. item is: import this
            # and import statement in collection is: import this, that
            if isinstance(item, ModuleImportStatement) and isinstance(imp_or_comment, ModuleImportStatement):
                matching_modules = all(mod in imp_or_comment.modules for mod in item.modules)
                matching_renames = all(rename in imp_or_comment.renames for rename in item.renames)
                if matching_modules and matching_renames:
                    return True

            # e.g. item is: from this import that
            # and import statement in collection is: from this import that, another
            if isinstance(item, ObjectImportStatement) and isinstance(imp_or_comment, ObjectImportStatement):
                matching_module = imp_or_comment.module == item.module
                matching_objs = all(mod in imp_or_comment.objs for mod in item.objs)
                matching_renames = all(rename in imp_or_comment.renames for rename in item.renames)
                if matching_module and matching_objs and matching_renames:
                    return True


        return False

    def __str__(self):
        return '\n'.join(str(imp) for imp in self)

    def obj_name_is_imported(self, obj_name: str) -> bool:

        obj_module: Optional[str]
        obj_name_parts = obj_name.split('.')
        if len(obj_name_parts) != 1:
            obj_module = '.'.join(obj_name_parts[:-1])
            obj_name = obj_name_parts[-1]
        else:
            # no . found, meaning object was imported by object import statement, no module name
            obj_module = None

        for imp_or_comment in self:
            if isinstance(imp_or_comment, Comment):
                continue # could not be imported from a comment
            if isinstance(imp_or_comment, ModuleImportStatement):
                if obj_module is None:
                    continue # object was imported by object import statement

                # object was imported by module import statement
                if (obj_module in imp_or_comment.modules) or (obj_module in imp_or_comment.renames.new_names):
                    return True # found matching module
            elif isinstance(imp_or_comment, ObjectImportStatement):
                if (obj_name in imp_or_comment.objs) or (obj_name in imp_or_comment.renames.new_names):
                    return True

        # failed all checks, obj not imported
        return False

    def get_import_for_ast_obj(self, obj_ast: ast.AST) -> ImportOrNone:
        possibly_imported_name = extract_external_name_from_assign_value(obj_ast)

        if possibly_imported_name is None:
            # Did not find any external names for this ast obj. Likely builtin.
            return None

        return self.get_import_for_module_or_obj_name(possibly_imported_name)

    def get_import_for_module_or_obj_name(self, name: str) -> ImportOrNone:
        found_import = False
        for imp in self:
            if isinstance(imp, ModuleImportStatement):
                if name in imp.modules:
                    # match on original module name
                    # set up for creating a new import
                    found_import = True
                    renames = None
                    modules = [name]
                elif name in imp.renames.new_names:
                    # match on renamed module name
                    # set up for creating a new import
                    found_import = True
                    renames = RenameStatementCollection(
                        # Pull the rename matching this name
                        [rename for rename in imp.renames if rename.new_name == name]
                    )
                    # grab original module matching this rename
                    modules = [renames.reverse_name_map[name]]
                if found_import:
                    # May be multiple modules imported in this one statement. Create a new statement with just this module
                    return ModuleImportStatement(modules=modules, renames=renames)
            elif isinstance(imp, ObjectImportStatement):
                if name in imp.objs:
                    # match on original object name
                    # set up for creating a new import
                    found_import = True
                    renames = None
                    objs = [name]
                elif name in imp.renames.new_names:
                    # match on renamed object name
                    # set up for creating a new import
                    found_import = True
                    renames = RenameStatementCollection(
                        # Pull the rename matching this name
                        [rename for rename in imp.renames if rename.new_name == name]
                    )
                    # grab original object matching this rename
                    objs = [renames.reverse_name_map[name]]
                if found_import:
                    # May be multiple objects imported in this one statement. Create a new statement with just this object
                    return ObjectImportStatement(objs, module=imp.module, renames=renames)
        raise NoImportMatchingNameException(f'could not find name {name} in {self}')

    @property
    def imported_names(self) -> List[str]:
        imported_names: List[str] = []
        for imp_or_comment in self:
            if isinstance(imp_or_comment, Comment):
                continue # could not be imported from a comment
            if isinstance(imp_or_comment, ModuleImportStatement):
                imported_names += imp_or_comment.modules
                imported_names += imp_or_comment.renames.new_names
            elif isinstance(imp_or_comment, ObjectImportStatement):
                imported_names += imp_or_comment.objs
                imported_names += imp_or_comment.renames.new_names
                imported_names.append(imp_or_comment.module)
        return list(set(imported_names)) # remove duplicates

    @property
    def modules(self):
        modules = []
        for item in self:
            # object import statements have one module
            if isinstance(item, ObjectImportStatement):
                modules.append(item.module)
            # module import statements can have multiple modules
            elif isinstance(item, ModuleImportStatement):
                modules += item.modules

        return modules

    @property
    def objs(self):
        objs = []
        for item in self:
            # only object import statements have objects
            if isinstance(item, ObjectImportStatement):
                objs += item.objs

        return objs

    # @property
    # def renames(self):
    #     renames = {}
    #     for item in self:
    #         item: AnyImportStatement
    #         renames[] = item.renames
    #
    #     return renames

