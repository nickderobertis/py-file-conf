from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.basemodels.config import ConfigBase

from pyfileconf.io.file.load.lazy.config import ConfigFileLoader
from pyfileconf.io.file.write.config import ConfigFileStr

class ConfigFileInterface(ConfigFileLoader):

    def save(self, config: 'ConfigBase'):
        file_str_obj = ConfigFileStr(
            config,
            existing_assigns=self.assigns,
            existing_imports=self.imports,
            existing_body=self.assignment_body
        )

        with open(self.filepath, 'w', newline='\n', encoding='utf8') as f:
            f.write(file_str_obj.file_str)