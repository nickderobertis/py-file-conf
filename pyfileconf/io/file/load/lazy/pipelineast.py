from pyfileconf.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader
from pyfileconf.io.file.load.parsers.assign import extract_assignment_from_ast_by_name

class PipelineAstLoader(ImportAssignmentLazyLoader):

    def load(self):
        # Get ast, imports, assigns
        super().register()

        # Store pipeline dict assignment
        if self._ast is not None:
            self._pipeline_dict_assign = extract_assignment_from_ast_by_name(self._ast, 'pipeline_dict')
        else:
            self._pipeline_dict_assign = None

        # TODO [#10]: parse modules in pipeline dict

    @property
    def pipeline_dict_assign(self):
        return self._try_getattr_else_load('_pipeline_dict_assign')

    def _try_getattr_else_load(self, attr: str):
        return self._try_getattr_else_call_func(attr, self.load)