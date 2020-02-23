from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyfileconf.basemodels.config import ConfigBase

from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.io.file.load.lazy.datadict import SpecificClassDictLoader
from pyfileconf.io.file.write.base import FileStr


class SpecificClassDictInterface(SpecificClassDictLoader):

    def save(self, config: 'ConfigBase'):
        # Set existing assigns and body to empty because should be completely replaced by new specific class dict
        file_str_obj = FileStr(
            config,
            existing_assigns=AssignmentStatementContainer([]),
            existing_imports=self.imports,
            existing_body=[]
        )

        with open(self.filepath, 'w', newline='\n', encoding='utf8') as f:
            f.write(file_str_obj.file_str)