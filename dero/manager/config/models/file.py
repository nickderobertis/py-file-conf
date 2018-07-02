import os
from copy import deepcopy
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from dero.manager.config.models.config import Config

from dero.manager.config.logic.load import _split_lines_into_import_and_assignment
from dero.manager.config.logic.write import dict_as_local_definitions_str, modules_and_items_as_imports_str
from dero.manager.sectionpath.sectionpath import _strip_py
from dero.manager.imports.models.tracker import ImportTracker
from dero.manager.imports.logic.load.file import get_user_defined_dict_from_filepath

class ConfigFile:
    """
    Represents config file on filesystem. Handles low-level functions for writing and reading config file
    """

    def __init__(self, filepath: str, name: str=None, loaded_modules=None):
        self.filepath = filepath

        if name is None:
            name = _strip_py(os.path.basename(filepath))

        self.name = name
        self._imports = []
        self._assigns = []
        self._loaded_modules = loaded_modules


    def load(self) -> 'Config':
        from dero.manager.config.models.config import Config

        # First import file, get user defined variables
        import_tracker = ImportTracker()
        config_dict = get_user_defined_dict_from_filepath(self.filepath)
        self._loaded_modules = deepcopy(import_tracker.imported_modules)

        # Now read file, to get as text rather than Python code
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        self._lines = lines
        self._imports, self._assigns = _split_lines_into_import_and_assignment(lines)

        return Config(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)


    @property
    def content(self):
        return '\n'.join(self._lines)

    def save(self, config: 'Config') -> None:
        file_str = self._config_to_file_str(config)

        with open(self.filepath, 'w') as f:
            f.write(file_str)

    def _config_to_file_str(self, config: 'Config') -> str:

        loaded_modules = self._get_loaded_modules(config)

        # Deal with imports as well as variable assignment
        if loaded_modules is not None:
            variable_assignment_section = dict_as_local_definitions_str(config, config._loaded_modules)
            imports_str = modules_and_items_as_imports_str(config._loaded_modules, config)
            return imports_str + variable_assignment_section

        # no loaded modules, just variable assignment
        variable_assignment_section = dict_as_local_definitions_str(config)

        return variable_assignment_section

    def _get_loaded_modules(self, config: 'Config') -> List[str]:
        if config._loaded_modules is not None:
            return config._loaded_modules
        elif self._loaded_modules is not None:
            return self._loaded_modules
        else:
            return None