from typing import Union

from pyfileconf.pipelines.models.collection import PipelineCollection
from pyfileconf.basemodels.registrar import Registrar
from pyfileconf.views.object import ObjectView

ObjectViewOrCollection = Union[ObjectView, PipelineCollection]

class PipelineRegistrar(Registrar):
    collection_class = PipelineCollection

    def get(self, section_path_str: str):
        obj_view_or_collection: ObjectViewOrCollection = super().get(section_path_str)

        # Nothing further needed for collections
        if isinstance(obj_view_or_collection, PipelineCollection):
            return obj_view_or_collection

        # Need to load ObjectView, return actual object
        return obj_view_or_collection.load()





