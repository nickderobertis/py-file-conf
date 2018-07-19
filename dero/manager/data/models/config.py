
from dero.manager.basemodels.config import ConfigBase
from dero.manager.data.models.source import DataSource, DataType
from dero.manager.data.models.file import DataConfigFile, ConfigFileBase
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer
from dero.manager.io.file.load.parsers.fromdict import extract_dict_from_ast_dict_or_dict_constructor
from dero.manager.data.models.astitems import ast_str, ast_dict_constructor


class DataConfig(ConfigBase):
    config_file_class = DataConfigFile

    def __init__(self, d: dict = None, name: str = None, annotations: dict = None,
                 imports: ImportStatementContainer = None,
                 _file: ConfigFileBase = None, begin_assignments: AssignmentStatementContainer = None,
                 active_config_dict: dict = None, **kwargs):

        if active_config_dict is None:
            active_config_dict = {}

        super().__init__(
            d=d,
            name=name,
            annotations=annotations,
            imports=imports,
            _file=_file,
            begin_assignments=begin_assignments,
            **kwargs
        )

        self.active_config_dict = active_config_dict


    @classmethod
    def from_source(cls, data_source: DataSource, name: str=None, imports: ImportStatementContainer = None):
        # Initialize a blank config dictionary
        config_dict = DataSource._scaffold_dict.copy()

        if data_source.loader_func_kwargs == {}:
            # If empty dict, must be where file doesn't exist, and so loader_func_kwargs were set to default
            # Need to convert to ast version
            data_source.loader_func_kwargs = ast_dict_constructor

        # Fill blank config dict
        for config_attr in config_dict:
            if not _source_attr_is_none(data_source, config_attr):
                config_dict[config_attr] = getattr(data_source, config_attr)

        # Special handling for name, which will be set even before creating file
        if isinstance(config_dict['name'], str):
            config_dict['name'] = ast_str(config_dict['name'])  # convert str to ast

        # Handle loader func kwargs. They are saved as a dict in data source, but when passing to
        # init, they are spread. Therefore save as their own items in config dict
        loader_func_kwargs = extract_dict_from_ast_dict_or_dict_constructor(data_source.loader_func_kwargs)
        for config_attr, config_value in loader_func_kwargs.items():
            config_dict[config_attr] = config_value

        return cls(config_dict, name=name, imports=imports)

def _source_attr_is_none(source: DataSource, source_attr: str) -> bool:
    source_value = getattr(source, source_attr, None)
    if source_value == None:  # using equals to call __eq__ method of DataType
        return True

    return False

