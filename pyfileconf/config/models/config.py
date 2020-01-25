
from pyfileconf.pipelines.models.config import FunctionConfig
from pyfileconf.config.models.file import ActiveFunctionConfigFile

class ActiveFunctionConfig(FunctionConfig):

    config_file_class = ActiveFunctionConfigFile