import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dero.manager.basemodels.config import ConfigBase

from dero.manager.sectionpath.sectionpath import _strip_py
from dero.manager.assignments.models.container import AssignmentStatementContainer
from dero.manager.io.file.interfaces.config import ConfigFileInterface


class ConfigFileBase:

    ##### Scaffolding functions or attributes. Need to override when subclassing  ####

    # lines to always import. pass import objects
    always_imports = []

    # assignment lines to always include at beginning. pass assignment objects
    always_assigns = []

    # class to use for interfacing with file
    interface_class = ConfigFileInterface

    ##### Base class functions and attributes below. Shouldn't usually need to override in subclassing #####

    def __init__(self, filepath: str, name: str=None, loaded_modules=None):
        self.interface = self.interface_class(filepath)

        if name is None:
            name = _strip_py(os.path.basename(filepath))

        self.name = name

    def load(self, config_class: type = None) -> 'ConfigBase':
        config_dict, annotation_dict = self.interface.load()

        if config_class is None:
            config_class = ConfigBase

        return config_class(
            d=config_dict,
            annotation_dict=annotation_dict,
            imports=self.interface.imports,
            _file=self
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

        # Add always assigns
        always_assigns = AssignmentStatementContainer(self.always_assigns)
        always_defaults, always_annotations = always_assigns.to_default_dict_and_annotation_dict()
        config.update(always_defaults)
        config.annotations.update(always_annotations)
