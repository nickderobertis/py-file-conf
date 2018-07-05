from typing import List

from dero.manager.basemodels.container import Container
from dero.mixins.repr import ReprMixin
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.interfaces import AnyImportStatement

class ImportStatementContainer(Container, ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: List[AnyImportStatement]):
        self.items = items

    def __contains__(self, item: AnyImportStatement):
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

