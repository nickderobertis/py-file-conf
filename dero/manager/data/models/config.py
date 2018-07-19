
from dero.manager.basemodels.config import ConfigBase
from dero.manager.data.models.source import DataSource
from dero.manager.data.models.file import DataConfigFile, ConfigFileBase
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer
from dero.manager.io.file.load.parsers.fromdict import extract_dict_from_ast_dict_or_dict_constructor


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
        config_dict = {attr: None for attr in DataSource._scaffold_items}

        # Fill blank config dict
        for config_attr in config_dict:
            if hasattr(data_source, config_attr):
                config_dict[config_attr] = getattr(data_source, config_attr)

        # Handle loader func kwargs. They are saved as a dict in data source, but when passing to
        # init, they are spread. Therefore save as their own items in config dict
        loader_func_kwargs = extract_dict_from_ast_dict_or_dict_constructor(data_source.loader_func_kwargs)
        for config_attr, config_value in loader_func_kwargs.items():
            config_dict[config_attr] = config_value

        return cls(config_dict, name=name, imports=imports)