import os
from copy import deepcopy
from typing import List, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from dero.manager.config.models.config import Config

from dero.manager.config.logic.load import (
    _split_lines_into_import_and_assignment,
    _split_assignment_line_into_variable_name_and_assignment
)
from dero.manager.config.logic.write import (
    dict_as_local_definitions_lines,
    modules_and_items_as_imports_lines,
    import_lines_as_str,
    assignment_lines_as_str
)
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
        self.imports = []
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
        self.imports, self.assigns = _split_lines_into_import_and_assignment(lines)

        return Config(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)


    @property
    def content(self):
        return '\n'.join(self._lines)

    def save(self, config: 'Config') -> None:
        import_lines, assignment_lines = self._config_to_file_lines(config)
        self._add_new_lines(import_lines, assignment_lines)
        file_str = self.file_str # access here, so that if error in assembling, will not overwrite file

        with open(self.filepath, 'w') as f:
            f.write(file_str)

    @property
    def file_str(self) -> str:
        return self._import_section + self._assignment_section

    @property
    def _import_section(self) -> str:
        return import_lines_as_str(self.imports)

    @property
    def _assignment_section(self) -> str:
        return assignment_lines_as_str(self._assigns)

    @property
    def assigned_variables(self) -> List[str]:

        if hasattr(self, '_assigned_variables'):
            return self._assigned_variables

        self._set_assigned_variables()
        return self._assigned_variables

    def _set_assigned_variables(self):
        assigned_variables = []
        for line in self._assigns:
            variable_name, value_repr = _split_assignment_line_into_variable_name_and_assignment(line)
            assigned_variables.append(variable_name)
        self._assigned_variables = assigned_variables

    @property
    def assigns(self):
        return self._assigns

    @assigns.setter
    def assigns(self, assigns: List[str]):
        self._assigns = assigns
        self._set_assigned_variables()

    def _add_new_lines(self, new_imports_lines: List[str], new_variable_assignment_lines: List[str]) -> None:
        # For import statements, just check if they already exist exactly as generated
        [_append_if_not_in_list(self.imports, line) for line in new_imports_lines]

        # For assignment statements, check if the variable name is already defined. Then don't add
        # the new line. Different handling as value may not be set correctly by code.
        for line in new_variable_assignment_lines:
            variable_name, value_repr = _split_assignment_line_into_variable_name_and_assignment(line)
            if variable_name is None:
                continue # whitespace line
            if variable_name not in self.assigned_variables:
                self.assigns.append(line)
                # need to trigger set so that assigned variables will update from self.assigns
                self._set_assigned_variables()

    def _config_to_file_lines(self, config: 'Config') -> Tuple[List[str], List[str]]:

        loaded_modules = self._get_loaded_modules(config)

        # Deal with imports as well as variable assignment
        if loaded_modules is not None:
            new_variable_assignment_lines = dict_as_local_definitions_lines(config, config._loaded_modules)
            new_imports_lines = modules_and_items_as_imports_lines(config._loaded_modules, config)
            return new_imports_lines, new_variable_assignment_lines

        # no loaded modules, just variable assignment
        new_variable_assignment_lines = dict_as_local_definitions_lines(config)

        return [], new_variable_assignment_lines

    def _get_loaded_modules(self, config: 'Config') -> List[str]:
        if config._loaded_modules is not None:
            return config._loaded_modules
        elif self._loaded_modules is not None:
            return self._loaded_modules
        else:
            return None

def _append_if_not_in_list(list_: List, item) -> None:
    if item not in list_:
        list_.append(item)