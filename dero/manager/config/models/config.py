
from dero.manager.pipelines.models.config import FunctionConfig
from dero.manager.config.models.file import ActiveFunctionConfigFile

class ActiveFunctionConfig(FunctionConfig):

    config_file_class = ActiveFunctionConfigFile