import os

from dero.mixins.repr import ReprMixin
from dero.manager.config.models.config import Config
from dero.manager.basemodels.container import Container
from dero.manager.logic.get import _get_public_name_or_special_name
from dero.manager.pipelines.models.interfaces import (
    PipelineDict,
    PipelinesOrFunctionsOrCollections,
    PipelineOrFunctionOrCollection,
    PipelineDictsOrPipelinesOrFunctions
)

class PipelineCollection(Container, ReprMixin):
    repr_cols = ['name', 'basepath', 'items']

    def __init__(self, basepath: str, items: PipelinesOrFunctionsOrCollections, name: str=None):
        self.basepath = basepath
        self.items = items
        self.name = name

    def __getattr__(self, item):
        return self.pipeline_map[item]

    def __dir__(self):
        return self.pipeline_map.keys()

    @property
    def pipeline_map(self):
        if hasattr(self, '_pipeline_map'):
            return self._pipeline_map

        self._set_pipeline_map()
        return self._pipeline_map

    def _set_pipeline_map(self):
        pipeline_map = {}
        for pipeline_or_collection in self:
            pipeline_name = _get_public_name_or_special_name(pipeline_or_collection)
            pipeline_map[pipeline_name] = pipeline_or_collection
        self._pipeline_map = pipeline_map

    @classmethod
    def from_pipeline_dict(cls, pipeline_dict: PipelineDict, basepath: str, name: str=None):
        items = []
        for section_name, dict_or_list in pipeline_dict:
            section_basepath = os.path.join(basepath, section_name)
            if isinstance(dict_or_list, dict):
                # Got another pipeline dict. Recursively process
                items.append(
                    PipelineCollection.from_pipeline_dict(dict_or_list, basepath=section_basepath, name=section_name)
                )
            elif isinstance(dict_or_list, list):
                # Got a list of functions or pipelines. Create a collection directly from items
                items.append(
                    PipelineCollection.from_pipeline_list(dict_or_list, basepath=section_basepath, name=section_name)
                )

        return cls(basepath=basepath, items=items, name=name)

    @classmethod
    def from_pipeline_list(cls, pipeline_list: PipelineDictsOrPipelinesOrFunctions, basepath: str, name: str=None):
        items = []
        for dict_or_item in pipeline_list:
            if isinstance(dict_or_item, dict):
                items.append(
                    PipelineCollection.from_pipeline_dict(dict_or_item, basepath=basepath, name=name)
                )
            else:
                # pipeline or function
                items.append(dict_or_item)

        return cls(basepath=basepath, items=items, name=name)


    def _output_config_files(self):
        [self._output_config_file(item) for item in self]

    def _output_config_file(self, item: PipelineOrFunctionOrCollection):
        if isinstance(item, PipelineCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with Pipeline or function
        item_name = _get_public_name_or_special_name(item)
        item_filepath = os.path.join(self.basepath, item_name)

        if os.path.exists(item_filepath):
            # TODO: update existing config file if arguments for function have changed.
            # must be able to do this without overriding the user's default arguments for the function
            return

        item_config = Config.from_pipeline_or_function(item)
        item_config.to_file(item_filepath)



