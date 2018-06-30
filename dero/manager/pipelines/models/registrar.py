
from dero.manager.logic.get import _get_from_nested_obj_by_section_path
from dero.manager.pipelines.models.collection import PipelineCollection
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.pipelines.models.interfaces import (
    PipelineDict,
    PipelineOrFunctionOrCollection
)

class PipelineRegistrar:

    def __init__(self, collection: PipelineCollection, basepath: str, name=None):
        self.collection = collection
        self.basepath = basepath
        self.name = name

    def __getattr__(self, item):
        return self.collection[item]

    def __dir__(self):
        return self.collection.keys()

    @classmethod
    def from_pipeline_dict(cls, pipeline_dict: PipelineDict, basepath: str, name: str=None):
        collection = PipelineCollection.from_pipeline_dict(pipeline_dict, basepath=basepath, name=name)

        return cls(collection, basepath=basepath, name=name)

    def scaffold_config(self):
        self.collection._output_config_files()

    def get(self, section_path_str: str) -> PipelineOrFunctionOrCollection:
        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final section or pipeline
        return _get_from_nested_obj_by_section_path(self, section_path)



