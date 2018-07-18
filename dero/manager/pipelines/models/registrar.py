
from dero.manager.pipelines.models.collection import PipelineCollection
from dero.manager.basemodels.registrar import Registrar
from dero.manager.views.object import ObjectView

class PipelineRegistrar(Registrar):
    collection_class = PipelineCollection

    def get(self, section_path_str: str):
        obj_view: ObjectView = super().get(section_path_str)

        # Need to load ObjectView, return actual object
        return obj_view.load()





