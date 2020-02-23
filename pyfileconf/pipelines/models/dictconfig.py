from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.basemodels.config import ConfigBase, ImportsAndAssigns
from pyfileconf.pipelines.models.dictfile import PipelineDictFile


class PipelineDictConfig(ConfigBase):

    config_file_class = PipelineDictFile

    def as_imports_and_assignments(self) -> ImportsAndAssigns:
        pipeline_dict_assign = AssignmentStatement.from_str(self['pipeline_dict'])
        assigns = AssignmentStatementContainer([pipeline_dict_assign])
        return self.imports, assigns

