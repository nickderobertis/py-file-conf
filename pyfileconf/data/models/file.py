from typing import TYPE_CHECKING, Optional, Type, Sequence

if TYPE_CHECKING:
    from pyfileconf.data.models.config import SpecificClassConfig

from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.io.file.interfaces.activeconfig import ActiveConfigFileInterface


class SpecificClassConfigFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = []

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = []

    def __init__(self, filepath: str, name: str = None, klass: Optional[Type] = None,
                 always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None):
        super().__init__(
            filepath,
            name=name,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs
        )

        # Override class definitions with object specific definitions
        # TODO: handle both object imports and module imports
        self.always_imports = [ObjectImportStatement.from_str(import_str) for import_str in self.always_import_strs]
        self.always_assigns = [AssignmentStatement.from_str(assign_str) for assign_str in self.always_assign_strs]

    def __call__(self, *args, **kwargs):
        """
        For compatibility with BaseConfig which expects to call class, while here an object will be used
        """
        # Create new object
        # Use defaults from this object
        obj_kwargs = dict(
            name=self.name,
            klass=self.klass,
            always_import_strs=self.always_import_strs,
            always_assign_strs=self.always_assign_strs
        )
        obj_kwargs.update(kwargs)
        obj = self.__class__(*args, **obj_kwargs)
        return obj

    def load(self, config_class: type = None) -> 'SpecificClassConfig':
        # Override base class method to pull a single dict, and not pass annotations
        from pyfileconf.data.models.config import SpecificClassConfig

        # Data configs are a hybrid of the ast/static config and the active config
        self.active_interface = ActiveConfigFileInterface(self.interface.filepath)

        config_dict, annotation_dict = self.interface.load()
        user_defined_dict = self.active_interface.load()

        if config_class is None:
            config_class = SpecificClassConfig

        return config_class(
            d=config_dict,
            annotations=annotation_dict,
            active_config_dict=user_defined_dict,
            imports=self.interface.imports,
            _file=self,
            name=self.name,
            klass=self.klass,
            always_assign_strs=self.always_assign_strs,
            always_import_strs=self.always_import_strs,
        )