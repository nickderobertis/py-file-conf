import os
from functools import partial
from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from dero.manager.basemodels.config import ConfigBase

from dero.manager.sectionpath.sectionpath import _strip_py

from dero.manager.config.logic.load import (
    _split_assignment_line_into_variable_name_and_assignment
)
from dero.manager.config.logic.write import (
    import_lines_as_str,
    assignment_lines_as_str
)
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.imports.models.statements.interfaces import AnyImportStatementOrComment, ObjectImportStatement
from dero.manager.io.file.interfaces.config import ConfigFileInterface


class ConfigFileBase:

    ##### Scaffolding functions or attributes. Need to override when subclassing  ####

    # lines to always import. pass import objects
    always_imports = []

    # assignment lines to always include at beginning. pass assignment objects
    always_assigns = []

    def load(self) -> 'ConfigBase':
        """

        Override this function when subclassing ConfigFileBase. Need to use self._load_into_config_dict,
        to get a dictionary of configuration, then create a Config instance from it. For example, see below:

        from dero.manager.config.models.config import FunctionConfig

        config_dict = self._load_into_config_dict()

        return FunctionConfig(config_dict, imports=imports, _file=self, name=self.name)

        """
        raise NotImplementedError('must use FunctionConfigFile.load or DataConfigFile.load, not ConfigFileBase.load')

    def _load_into_config_dict(self) -> dict:
        """

        Assigns to self._loaded_modules, self._lines, self.imports, self.assigns
        Returns: config_dict

        """
        raise NotImplementedError('must use FunctionConfigFile._load_into_config_dict or '
                                  'DataConfigFile._load_into_config_dict, not ConfigFileBase._load_into_config_dict')

    def _config_to_file_lines(self, config: 'ConfigBase') -> Tuple[List[str], List[str]]:
        """

        Args:
            config:

        Returns:

        """
        raise NotImplementedError('must use FunctionConfigFile._config_to_file_lines or'
                                  ' DataConfigFile._config_to_file_lines, not ConfigFileBase._config_to_file_lines')

    ##### Base class functions and attributes below. Shouldn't usually need to override in subclassing #####

    def __init__(self, filepath: str, name: str=None, loaded_modules=None):
        self.filepath = filepath

        if name is None:
            name = _strip_py(os.path.basename(filepath))

        self.name = name
        self.imports = ImportStatementContainer([])
        self._assigns = []
        self._loaded_modules = loaded_modules

    @property
    def content(self):
        return '\n'.join(self._lines)

    def save(self, config: 'ConfigBase') -> None:
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
    def imported_variables(self):
        if hasattr(self, '_imported_variables'):
            return self._imported_variables

        self._set_imported_variables()
        return self._imported_variables

    def _set_imported_variables(self):
        self._imported_variables = self.imports.imported_names

    @property
    def assigns(self):
        return self._assigns

    @assigns.setter
    def assigns(self, assigns: List[str]):
        self._assigns = assigns
        self._set_assigned_variables()

    @property
    def imports(self):
        return self._imports

    @imports.setter
    def imports(self, imports: List[str]):
        self._imports = imports
        self._set_imported_variables()

    @property
    def all_variables(self):
        return self.imported_variables + self.assigned_variables

    def _add_new_lines(self, new_imports_lines: List[AnyImportStatementOrComment], new_variable_assignment_lines: List[str]) -> None:

        always_imports = self.always_imports.copy()
        always_assigns_begin = self.always_assigns_begin.copy()
        always_assigns_end = self.always_assigns_end.copy()

        # For import statements, just check if they already exist exactly as generated
        self._add_import_objs_if_not_in_imports(new_imports_lines)

        # Add always imports
        always_imports.reverse() # are getting added to beginning, so reverse order first to maintain order
        self._add_import_objs_if_not_in_imports(always_imports, beginning=True)

        # Add always assigns
        always_assigns_begin.reverse() # are getting added to beginning, so reverse order first to maintain order
        self._add_assignment_lines_if_not_in_variables(always_assigns_begin, beginning=True)

        # For assignment statements, check if the variable name is already defined. Then don't add
        # the new line. Different handling as value may not be set correctly by code.
        self._add_assignment_lines_if_not_in_variables(new_variable_assignment_lines)

        # Finally, add always assigns end
        self._add_assignment_lines_if_not_in_variables(always_assigns_end)

    def _add_assignment_lines_if_not_in_variables(self, lines: List[str], beginning: bool=False) -> None:
        [self._add_assignment_line_if_not_in_variables(line, beginning=beginning) for line in lines]

    def _add_assignment_line_if_not_in_variables(self, line: str, beginning: bool=False) -> None:
        if beginning:
            add_func = partial(self.assigns.insert, 0)
        else:
            add_func = self.assigns.append

        variable_name, value_repr = _split_assignment_line_into_variable_name_and_assignment(line)
        if variable_name is None:
            return  # whitespace line
        if variable_name not in self.all_variables:
            add_func(line)
            # need to trigger set so that assigned variables will update from self.assigns
            self._set_assigned_variables()

    def _add_import_objs_if_not_in_imports(self, import_objs: List[AnyImportStatementOrComment], beginning: bool=False) -> None:
        [self._add_import_obj_if_not_in_imports(import_obj, beginning=beginning) for import_obj in import_objs]

    def _add_import_obj_if_not_in_imports(self, import_obj: AnyImportStatementOrComment, beginning: bool=False) -> None:
        if isinstance(import_obj, ObjectImportStatement):
            imported_objs = import_obj.objs
            already_imported = lambda: all([self.imports.obj_name_is_imported(imp_obj) for imp_obj in imported_objs])
        else:
            already_imported = lambda: import_obj in self.imports

        if not already_imported():
            if beginning:
                add_func = partial(self.imports.insert, 0)
            else:
                add_func = self.imports.append
            add_func(import_obj)
            self._set_imported_variables()

    def _get_loaded_modules(self, config: 'ConfigBase') -> List[str]:
        if config._loaded_modules is not None:
            return config._loaded_modules
        elif self._loaded_modules is not None:
            return self._loaded_modules
        else:
            return None

def _append_if_not_in_list(list_: List, item) -> None:
    if item not in list_:
        list_.append(item)
