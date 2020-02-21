from typing import Optional, Type, Any, Sequence, Union

from pyfileconf.basemodels.config import ConfigBase
from pyfileconf.data.models.file import SpecificClassConfigFile, ConfigFileBase
from pyfileconf.imports.logic.load.klass import class_function_args_as_dict
from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.data.models.astitems import ast_str, ast_none


class SpecificClassConfig(ConfigBase):
    config_file_class: Union[SpecificClassConfigFile, Type[ConfigFileBase]]  # type: ignore

    def __init__(self, d: dict = None, name: str = None, annotations: dict = None,
                 imports: ImportStatementContainer = None,
                 _file: ConfigFileBase = None, begin_assignments: AssignmentStatementContainer = None,
                 active_config_dict: dict = None, always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                 file_path: Optional[str] = None, **kwargs):

        if active_config_dict is None:
            active_config_dict = {}

        self.config_file_class = SpecificClassConfigFile(
            file_path,  # type: ignore
            name=name,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs
        )

        super().__init__(
            d=d,
            name=name,
            annotations=annotations,
            imports=imports,
            _file=_file,
            begin_assignments=begin_assignments,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs,
            **kwargs
        )

        self.active_config_dict = active_config_dict


    @classmethod
    def from_obj(cls, obj: Any, klass: Type, name: str=None, imports: ImportStatementContainer = None,
                 always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None, file_path: Optional[str] = None,
                 key_attr: str = 'name'):
        # Initialize a blank config dictionary
        config_dict = class_function_args_as_dict(klass)

        # Replace obj None with ast None
        config_dict = {key: value if value is not None else ast_none for key, value in config_dict.items()}

        # Fill blank config dict
        for config_attr in config_dict:
            if not _obj_attr_is_none(obj, config_attr):
                config_dict[config_attr] = getattr(obj, config_attr)

        # Special handling for name, which will be set even before creating file
        if isinstance(config_dict[key_attr], str):
            config_dict[key_attr] = ast_str(config_dict[key_attr])  # convert str to ast

        return cls(
            config_dict,
            name=name,
            imports=imports,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs,
            file_path=file_path
        )




def _obj_attr_is_none(obj: Any, source_attr: str) -> bool:
    source_value = getattr(obj, source_attr, None)
    if source_value is None:
        return True

    return False
