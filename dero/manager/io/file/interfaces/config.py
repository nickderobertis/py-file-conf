from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.basemodels.config import ConfigBase

from dero.manager.io.file.load.lazy.config import ConfigFileLoader
from dero.manager.io.file.write.config import ConfigFileStr

class ConfigFileInterface(ConfigFileLoader):

    def save(self, config: 'ConfigBase'):
        file_str_obj = ConfigFileStr(
            config,
            existing_assigns=self.assigns,
            existing_imports=self.imports,
            existing_body=self.assignment_body
        )

        with open(self.filepath, 'w') as f:
            f.write(file_str_obj.file_str)