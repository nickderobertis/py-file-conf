from typing import Callable, Optional, Type, Sequence

from pyfileconf.basemodels.config import ConfigBase
from pyfileconf.imports.logic.load.func import function_args_as_dict
from pyfileconf.config.models.file import FunctionConfigFile

class FunctionConfig(ConfigBase):

    config_file_class = FunctionConfigFile

    @classmethod
    def from_file(cls, filepath: str, name: str = None,
                  klass: Optional[Type] = None, always_import_strs: Optional[Sequence[str]] = None,
                  always_assign_strs: Optional[Sequence[str]] = None):
        file = cls.config_file_class(
            filepath,
            name=name,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs
        )
        return file.load(cls)

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