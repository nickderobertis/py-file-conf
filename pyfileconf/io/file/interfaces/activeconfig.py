
from pyfileconf.io.file.load.active.loader import ActiveConfigFileLoader

class ActiveConfigFileInterface(ActiveConfigFileLoader):

    def save(self):
        raise NotImplementedError('call save with ConfigFileInterface, not ActiveConfigFileInterface')