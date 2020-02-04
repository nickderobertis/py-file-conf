
from pyfileconf.basemodels.registrar import Registrar
from pyfileconf.data.models.collection import SpecificClassCollection

class SpecificRegistrar(Registrar):
    collection_class = SpecificClassCollection

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.klass is None:
            raise ValueError('must pass class for SpecificRegistrar')
