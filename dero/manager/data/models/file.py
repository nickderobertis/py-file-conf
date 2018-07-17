from typing import TYPE_CHECKING, Tuple, List
if TYPE_CHECKING:
    from dero.manager.data.models.config import DataConfig

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.logic.parse.main import parse_import_lines_return_import_models
from dero.manager.imports.models.statements.interfaces import AnyImportStatementOrComment
from dero.manager.imports.logic.load.file import get_user_defined_dict_from_filepath
from dero.manager.config.logic.load import (
    _split_lines_into_import_and_assignment
)
from dero.manager.config.logic.write import (
    dict_as_local_definitions_lines,
    modules_and_items_as_imports_lines,
)
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.imports.models.statements.obj import ObjectImportStatement




class DataConfigFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = [ObjectImportStatement.from_str('from dero.manager import Selector')]

    # assignment lines to always include at beginning. pass strs
    always_assigns_begin = ['s = Selector()']

    # assignment lines to always include at end. pass strs
    always_assigns_end = ['loader_func_kwargs = dict(\n    \n)']

    def load(self) -> 'DataConfig':
        from dero.manager.data.models.config import DataConfig

        config_dict = self._load_into_config_dict()

        return DataConfig(config_dict, _loaded_modules=self._loaded_modules, _file=self, name=self.name)

    def _config_to_file_lines(self, config: 'DataConfig') -> Tuple[ImportStatementContainer, List[str]]:

        loaded_modules = self.imports.modules

        # Deal with imports as well as variable assignment
        if loaded_modules is not None:
            new_variable_assignment_lines = dict_as_local_definitions_lines(config, loaded_modules)
            new_imports_lines = modules_and_items_as_imports_lines(loaded_modules, config)
            new_imports = parse_import_lines_return_import_models(new_imports_lines)
            return new_imports, new_variable_assignment_lines

            # no loaded modules, just variable assignment
        new_variable_assignment_lines = dict_as_local_definitions_lines(config)

        return ImportStatementContainer([]), new_variable_assignment_lines

    def _load_into_config_dict(self) -> dict:
        # First import file, get user defined variables
        config_dict = get_user_defined_dict_from_filepath(self.filepath)

        # Now read file, to get as text rather than Python code
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        self._lines = lines
        import_lines, self.assigns = _split_lines_into_import_and_assignment(lines)
        self.imports = parse_import_lines_return_import_models(import_lines)

        return config_dict