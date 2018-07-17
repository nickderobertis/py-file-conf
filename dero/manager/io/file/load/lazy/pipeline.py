from dero.manager.io.file.load.lazy.pipelineast import PipelineAstLoader

class PipelineLoader(PipelineAstLoader):

    def load(self):
        # Get pipeline_dict_ast
        super().load()



    def _pipeline_dict_assign_to_dict(self):
        """
        Iterates through ast tree of pipeline dict, producing a dict/list structure, while leaving
        other objects as ast representations

        Returns:

        """