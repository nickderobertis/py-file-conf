from typing import Callable, Mapping, _KT, _VT

from dero.manager.config.logic.load.file import get_user_defined_dict_from_module, load_file_as_module
from dero.manager.config.logic.load.func import function_args_as_dict
from dero.manager.config.logic.write import dict_as_local_definitions_str


class Config(dict):

    def update(self, __m: Mapping[_KT, _VT], **kwargs: _VT):
        super().update(__m, **kwargs)
        self._update_file_str()

    def to_file(self, filepath: str):
        with open(filepath, 'w') as f:
            f.write(self.file_str)

    @property
    def file_str(self):
        try:
            return self._file_str
        except AttributeError:
            self._file_str = dict_as_local_definitions_str(self)

        return self._file_str

    @classmethod
    def from_file(cls, filepath: str):
        module = load_file_as_module(filepath)
        config_dict = get_user_defined_dict_from_module(module)

        return cls(config_dict)

    @classmethod
    def from_function(cls, func: Callable):
        config_dict = function_args_as_dict(func)

        return cls(config_dict)

    def _update_file_str(self):
        # only update if already set
        if hasattr(self, '_file_str'):
            self._file_str = dict_as_local_definitions_str(self)