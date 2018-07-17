from dero.manager.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader

class ConfigFileLoader(ImportAssignmentLazyLoader):

    def load(self):
        # Get ast, imports, assigns
        super().load()

        # Parse assigns into config dict