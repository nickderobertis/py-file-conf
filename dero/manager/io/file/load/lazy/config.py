from dero.manager.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader

class ConfigFileLoader(ImportAssignmentLazyLoader):

    def load(self) -> dict:
        # Get ast, imports, assigns
        super().load()

        # Parse assigns into config dict
        config_dict = self.assigns.to_dict()

        return config_dict