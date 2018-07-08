
from dero.manager.basemodels.registrar import Registrar
from dero.manager.data.models.collection import DataCollection

class DataRegistrar(Registrar):
    collection_class = DataCollection
