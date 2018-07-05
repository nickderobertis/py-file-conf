from copy import deepcopy
from typing import TYPE_CHECKING, Tuple, List
if TYPE_CHECKING:
    from dero.manager.config.models.config import FunctionConfig

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.tracker import ImportTracker
from dero.manager.imports.logic.load.file import get_user_defined_dict_from_filepath
from dero.manager.config.logic.load import (
    _split_lines_into_import_and_assignment
)
from dero.manager.config.logic.write import (
    dict_as_local_definitions_lines,
    modules_and_items_as_imports_lines,
)

class FunctionConfigFile(ConfigFileBase):
    """
    Represents config file on filesystem. Handles low-level functions for writing and reading config file
    """

    def load(self) -> 'FunctionConfig':
        from dero.manager.config.models.config import FunctionConfig

        config_dict = self._load_into_config_dict()

        return FunctionConfig(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)

    def _config_to_file_lines(self, config: 'FunctionConfig') -> Tuple[List[str], List[str]]:

        loaded_modules = self._get_loaded_modules(config)

        # Deal with imports as well as variable assignment
        if loaded_modules is not None:
            new_variable_assignment_lines = dict_as_local_definitions_lines(config, config._loaded_modules)
            new_imports_lines = modules_and_items_as_imports_lines(config._loaded_modules, config)
            return new_imports_lines, new_variable_assignment_lines

        # no loaded modules, just variable assignment
        new_variable_assignment_lines = dict_as_local_definitions_lines(config)

        return [], new_variable_assignment_lines

    def _load_into_config_dict(self) -> dict:
        # First import file, get user defined variables
        import_tracker = ImportTracker()
        config_dict = get_user_defined_dict_from_filepath(self.filepath)
        self._loaded_modules = deepcopy(import_tracker.imported_modules)

        # Now read file, to get as text rather than Python code
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        self._lines = lines
        self.imports, self.assigns = _split_lines_into_import_and_assignment(lines)

        return config_dict

