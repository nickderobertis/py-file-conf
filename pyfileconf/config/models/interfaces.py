from typing import Union

from pyfileconf.config.models.file import ActiveFunctionConfigFile
from pyfileconf.config.models.section import ConfigSection, ActiveFunctionConfig


ConfigSectionOrConfig = Union[ConfigSection, ActiveFunctionConfigFile, ActiveFunctionConfig]