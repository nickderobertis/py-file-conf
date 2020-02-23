from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.io.file.interfaces.datadict import SpecificClassDictInterface

class SpecificClassDictFile(ConfigFileBase):
    # lines to always import. pass import objects
    # no need to override default
    # always_imports = []

    # assignment lines to always include at beginning. pass assign objects
    # no need to override default
    # always_assigns = []

    # class to use for interfacing with file
    # no need to override default
    interface_class = SpecificClassDictInterface

    def load(self) -> dict:  # type: ignore
        return self.interface.load()