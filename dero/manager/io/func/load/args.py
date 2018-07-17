
from dero.manager.imports.models.statements.obj import ObjectImportStatement

class FunctionArgsExtractor:

    def __init__(self, object_import: ObjectImportStatement):
        self.object_import = object_import

    def extract_args(self):
        pass