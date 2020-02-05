import os
from typing import TYPE_CHECKING, List, Dict, Type, Optional, Sequence

from pyfileconf.assignments.models.statement import AssignmentStatement
from pyfileconf.imports.models.statements.interfaces import AnyImportStatement

if TYPE_CHECKING:
    from pyfileconf.basemodels.config import ConfigBase

from pyfileconf.sectionpath.sectionpath import _strip_py
from pyfileconf.assignments.models.container import AssignmentStatementContainer
from pyfileconf.io.file.interfaces.config import ConfigFileInterface


class ConfigFileBase:

    ##### Scaffolding functions or attributes. Need to override when subclassing  ####

    # lines to always import. pass import objects
    always_imports: List[AnyImportStatement] = []

    # assignment lines to always include at beginning. pass assignment objects
    always_assigns: List[AssignmentStatement] = []

    # always assign dict, where assigns will get added if item name matches dict key
    always_assign_with_names_dict: Dict[str, List[AssignmentStatement]] = {}

    # class to use for interfacing with file
    interface_class = ConfigFileInterface

    ##### Base class functions and attributes below. Shouldn't usually need to override in subclassing #####

    def __init__(self, filepath: str, name: str=None, klass: Optional[Type] = None,
                 always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None):
        self.interface = self.interface_class(filepath)

        # TODO [#23]: check if setting filepath in ConfigFileBase.__init__ had side effects
        #
        # added this because filepath was being set after object creation in
        # `pyfileconf.basemodels.config.ConfigBase.to_file` and was causing mypy errors. Check
        # to ensure this didn't cause any issues.
        self.filepath = filepath

        if name is None:
            name = _strip_py(os.path.basename(filepath))

        self.name = name
        self.klass = klass
        self.always_import_strs = always_import_strs
        self.always_assign_strs = always_assign_strs

    def load(self, config_class: type = None) -> 'ConfigBase':
        from pyfileconf.basemodels.config import ConfigBase
        config_dict, annotation_dict = self.interface.load()

        if config_class is None:
            config_class = ConfigBase

        return config_class(
            d=config_dict,
            annotations=annotation_dict,
            imports=self.interface.imports,
            _file=self,
            name=self.name,
            klass=self.klass,
            always_import_strs=self.always_import_strs,
            always_assign_strs=self.always_assign_strs,
        )

    def save(self, config: 'ConfigBase') -> None:
        self._add_always_imports_and_assigns_to_config(config)
        self.interface.save(config)

    def _add_always_imports_and_assigns_to_config(self, config: 'ConfigBase'):
        """
        Note: inplace
        """
        # Add always imports
        [config.imports.add_if_missing(imp) for imp in self.always_imports]

        # # Check if there are any extra assigns for items with this name
        always_assigns = self.always_assigns.copy()
        if self.name in self.always_assign_with_names_dict:
            always_assigns.extend(self.always_assign_with_names_dict[self.name])

        # Add always assigns
        # First handle begin assigns
        begin_assigns = AssignmentStatementContainer(
            [assign for assign in always_assigns if assign.prefer_beginning]
        )
        config.begin_assignments = begin_assigns
        # Now handle the rest
        # First get always assigns, annotations as dict
        other_always_assigns = AssignmentStatementContainer(
            [assign for assign in always_assigns if not assign.prefer_beginning]
        )
        always_defaults, always_annotations = other_always_assigns.to_default_dict_and_annotation_dict()
        # Select assigns, annotations which are not already defined in config
        new_defaults = {key: value for key, value in always_defaults.items() if key not in config}
        new_annotations = {key: value for key, value in always_annotations.items() if key not in config.annotations}
        # Add to config
        config.update(new_defaults)
        config.annotations.update(new_annotations)
