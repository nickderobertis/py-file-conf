from dero.manager.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader

class PipelineAstLoader(ImportAssignmentLazyLoader):

    def load(self):
        # Get ast, imports, assigns
        super().register()

        # Store pipeline dict assignment

        # TODO: parse modules in pipeline dict

    @property
    def pipeline_dict_assign(self):
        return self._try_getattr_else_load('_pipeline_dict_assign')

    def _try_getattr_else_load(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.load)