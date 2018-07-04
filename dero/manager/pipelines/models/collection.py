import os

from dero.mixins.repr import ReprMixin
from dero.manager.config.models.config import Config
from dero.manager.logic.get import _get_public_name_or_special_name
from dero.manager.pipelines.models.interfaces import (
    PipelineDict,
    PipelinesOrFunctionsOrCollections,
    PipelineOrFunctionOrCollection,
    PipelineDictsOrPipelinesOrFunctions,
    StrList
)
from dero.manager.basemodels.collection import Collection

class PipelineCollection(Collection, ReprMixin):
    repr_cols = ['name', 'basepath', 'items']

    def __init__(self, basepath: str, items: PipelinesOrFunctionsOrCollections, name: str=None,
                 loaded_modules: StrList=None):
        self.basepath = basepath
        self.items = items
        self.name = name
        self._loaded_modules = loaded_modules

    def __getattr__(self, item):
        return self.pipeline_map[item]

    def __dir__(self):
        return self.pipeline_map.keys()

    def _set_pipeline_map(self):
        pipeline_map = {}
        for pipeline_or_collection in self:
            pipeline_name = _get_public_name_or_special_name(pipeline_or_collection)
            pipeline_map[pipeline_name] = pipeline_or_collection
        self.pipeline_map = pipeline_map

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        self._items = items
        self._set_pipeline_map() # need to recreate pipeline map when items change

    @classmethod
    def from_pipeline_dict(cls, pipeline_dict: PipelineDict, basepath: str, name: str=None,
                           loaded_modules: StrList=None):
        items = []
        for section_name, dict_or_list in pipeline_dict.items():
            section_basepath = os.path.join(basepath, section_name)
            if isinstance(dict_or_list, dict):
                # Got another pipeline dict. Recursively process
                items.append(
                    PipelineCollection.from_pipeline_dict(
                        dict_or_list, basepath=section_basepath, name=section_name, loaded_modules=loaded_modules
                    )
                )
            elif isinstance(dict_or_list, list):
                # Got a list of functions or pipelines. Create a collection directly from items
                items.append(
                    PipelineCollection.from_pipeline_list(
                        dict_or_list, basepath=section_basepath, name=section_name, loaded_modules=loaded_modules
                    )
                )

        return cls(basepath=basepath, items=items, name=name)

    @classmethod
    def from_pipeline_list(cls, pipeline_list: PipelineDictsOrPipelinesOrFunctions, basepath: str, name: str=None,
                           loaded_modules: StrList=None):
        items = []
        for dict_or_item in pipeline_list:
            if isinstance(dict_or_item, dict):
                items.append(
                    PipelineCollection.from_pipeline_dict(
                        dict_or_item, basepath=basepath, name=name, loaded_modules=loaded_modules
                    )
                )
            else:
                # pipeline or function
                items.append(dict_or_item)

        return cls(basepath=basepath, items=items, name=name, loaded_modules=loaded_modules)


    def _output_config_files(self):

        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        self._output_section_config_file()
        [self._output_config_file(item) for item in self]

    def _output_config_file(self, item: PipelineOrFunctionOrCollection):
        if isinstance(item, PipelineCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with Pipeline or function
        item_name = _get_public_name_or_special_name(item) + '.py'
        item_filepath = os.path.join(self.basepath, item_name)

        if os.path.exists(item_filepath):
            # if config file already exists, load confguration from file, use to update function defaults
            existing_config = Config.from_file(item_filepath)
        else:
            existing_config = Config()

        item_config = Config.from_pipeline_or_function(item, loaded_modules=self._loaded_modules)
        item_config.update(existing_config) # override function defaults with any settings from file
        item_config.to_file(item_filepath)

    def _output_section_config_file(self):
        """
        creates a blank config file for the section
        """
        outpath = os.path.join(self.basepath, 'section.py')

        if os.path.exists(outpath):
            # Never overwrite section config.
            return

        with open(outpath, 'w') as f:
            f.write('\n')



