from dero.manager.io.file.load.lazy.pipelineast import PipelineAstLoader
from dero.manager.io.file.load.parsers.collections import extract_collections_from_ast

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
        self._pipeline_dict = extract_collections_from_ast(self.pipeline_dict_assign)
