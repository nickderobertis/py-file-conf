from typing import List

from dero.manager.basemodels.container import Container
from dero.manager.imports.models.statements.obj import ObjectImportStatement
from dero.manager.imports.models.statements.module import ModuleImportStatement
from dero.manager.imports.models.statements.interfaces import AnyImportStatement

class ImportStatementContainer(Container):

    def __init__(self, items: List[AnyImportStatement]):
        self.items = items

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

