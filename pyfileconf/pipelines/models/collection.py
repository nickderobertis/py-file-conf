import os

from pyfileconf.pipelines.models.config import FunctionConfig
from pyfileconf.logic.get import _get_public_name_or_special_name
from pyfileconf.pipelines.models.interfaces import ObjectViewOrCollection
from pyfileconf.views.object import ObjectView

from pyfileconf.basemodels.collection import Collection

class PipelineCollection(Collection):

    def _set_name_map(self):
        pipeline_map = {}
        for pipeline_or_collection in self:
            pipeline_name = _get_public_name_or_special_name(pipeline_or_collection)
            pipeline_map[pipeline_name] = pipeline_or_collection
        self.name_dict = pipeline_map

    def _transform_item(self, item):
        """
        Is called on each item when adding items to collection. Should handle whether the item
        is an actual item or another collection. Must return the item or collection.

        If not overridden, will just store items as is.

        Returns: item or Collection

        """
        if isinstance(item, PipelineCollection):
            # no processing needed for collections, just items
            return item

        # If item, convert to object view
        return ObjectView.from_ast_and_imports(item, self.imports)

    def _output_config_files(self):

        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        self._output_section_config_file()
        [self._output_config_file(item) for item in self]

    def _output_config_file(self, item: ObjectViewOrCollection):
        if isinstance(item, PipelineCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        if not isinstance(item, ObjectView):
            raise ValueError(f'did not initialize pipeline dict correctly. expected ObjectView, got {item} of '
                             f'type {type(item)}')

        # Dealing with ObjectView
        item_filepath = os.path.join(self.basepath, item.output_name + '.py')

        if os.path.exists(item_filepath):
            # if config file already exists, load confguration from file, use to update function defaults
            existing_config = FunctionConfig.from_file(item_filepath, item.output_name)
        else:
            existing_config = FunctionConfig()

        item_config = item.default_config.copy()
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



