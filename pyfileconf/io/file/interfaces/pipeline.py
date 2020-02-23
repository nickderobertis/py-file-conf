from typing import TYPE_CHECKING

from pyfileconf.assignments.models.container import AssignmentStatementContainer

if TYPE_CHECKING:
    from pyfileconf.basemodels.config import ConfigBase
from pyfileconf.io.file.load.lazy.pipeline import PipelineDictLoader
from pyfileconf.io.file.write.base import FileStr


class PipelineDictInterface(PipelineDictLoader):

    def save(self, config: 'ConfigBase'):
        # Set existing assigns and body to empty because should be completely replaced by new pipeline dict
        file_str_obj = FileStr(
            config,
            existing_assigns=AssignmentStatementContainer([]),
            existing_imports=self.imports,
            existing_body=[]
        )

        with open(self.filepath, 'w', newline='\n', encoding='utf8') as f:
            f.write(file_str_obj.file_str)