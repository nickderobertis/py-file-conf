from typing import TYPE_CHECKING, Optional, Type, Sequence

from pyfileconf.exceptions.imports import ExtractedIncorrectTypeOfImportException
from pyfileconf.imports.models.statements.module import ModuleImportStatement

if TYPE_CHECKING:
    from pyfileconf.data.models.config import SpecificClassConfig

from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.io.file.interfaces.activeconfig import ActiveConfigFileInterface


class SpecificClassConfigFile(ConfigFileBase):
    # lines to always import. pass import objects
    always_imports = [
        ObjectImportStatement.from_str('from pyfileconf import Selector', preferred_position='begin')
    ]

    # assignment lines to always include at beginning. pass assign objects
    always_assigns = [
        AssignmentStatement.from_str('s = Selector()', preferred_position='begin'),
    ]

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
        # Override class definitions with object specific definitions, if specifics are passed
        if self.always_import_strs:
            imports = []
            for import_str in self.always_import_strs:
                try:
                    imports.append(ObjectImportStatement.from_str(import_str))
                except ExtractedIncorrectTypeOfImportException:
                    imports.append(ModuleImportStatement.from_str(import_str))
            self.always_imports = imports
        elif self.always_import_strs == []:
            # None passed, remove default imports
            self.always_imports = []

        if self.always_assign_strs:
            self.always_assigns = [AssignmentStatement.from_str(assign_str) for assign_str in self.always_assign_strs]
        elif self.always_assign_strs == []:
            # None passed, remove default assignments
            self.always_assigns = []


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