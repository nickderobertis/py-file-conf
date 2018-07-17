from dero.manager.io.file.load.lazy.config import ConfigFileLoader
from dero.manager.io.file.write.config import ConfigFileStr
from dero.manager.basemodels.config import ConfigBase

class ConfigFileInterface(ConfigFileLoader):

    def save(self, config: ConfigBase):
        file_str = ConfigFileStr(
            config,
            existing_assigns=self.assigns,
            existing_imports=self.imports,
            existing_body=self.assignment_body
        )

        with open(self.filepath, 'w') as f:
            f.write(file_str)