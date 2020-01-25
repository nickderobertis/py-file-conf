from pyfileconf.io.file.load.lazy.pipelineast import PipelineAstLoader
from pyfileconf.io.file.load.parsers.collections import extract_collection_from_ast

class PipelineDictLoader(PipelineAstLoader):

    def load(self):
        # Get pipeline_dict_ast
        super().load()

        # Convert ast dicts and ast lists to normal dicts and lists, store as self.pipeline_dict
        self._pipeline_dict_assign_to_dict()

        return self.pipeline_dict

    @property
    def pipeline_dict(self):
        return self._try_getattr_else_load('_pipeline_dict')

    def _pipeline_dict_assign_to_dict(self):
        """
        Iterates through ast tree of pipeline dict, producing a dict/list structure, while leaving
        other objects as ast representations

        Returns:

        """
        if self.pipeline_dict_assign is not None:
            self._pipeline_dict = extract_collection_from_ast(self.pipeline_dict_assign.to_ast())
        else:
            self._pipeline_dict = {}
