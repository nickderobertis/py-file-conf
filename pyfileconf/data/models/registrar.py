
from pyfileconf.basemodels.registrar import Registrar
from pyfileconf.data.models.collection import DataCollection

class DataRegistrar(Registrar):
    collection_class = DataCollection
