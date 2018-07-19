from typing import Union

from dero.manager.pipelines.models.collection import PipelineCollection
from dero.manager.basemodels.registrar import Registrar
from dero.manager.views.object import ObjectView

ObjectViewOrCollection = Union[ObjectView, PipelineCollection]

class PipelineRegistrar(Registrar):
    collection_class = PipelineCollection

    def get(self, section_path_str: str):
        obj_view_or_collection: ObjectViewOrCollection = super().get(section_path_str)

        # Nothing futher needed for collections
        if isinstance(obj_view_or_collection, PipelineCollection):
            return obj_view_or_collection

        # Need to load ObjectView, return actual object
        return obj_view_or_collection.load()





