from typing import Callable, Any, List
import inspect

from dero.manager.basemodels.config import ConfigBase
from dero.manager.imports.logic.load.func import function_args_as_dict
from dero.manager.basemodels.pipeline import Pipeline
from dero.manager.config.models.file import FunctionConfigFile

class FunctionConfig(ConfigBase):

    config_file_class = FunctionConfigFile

    def for_function(self, func: Callable) -> dict:
        """
        Strips out items of config which are not applicable to function. Returns dictionary
        of config items for passing to the function.

        Args:
            func: func for which to filter out config items

        Returns: dict, applicable config for func
        """
        # Only pass items in config which are arguments of function
        func_kwargs = function_args_as_dict(func)
        return {key: value for key, value in self.items() if key in func_kwargs}