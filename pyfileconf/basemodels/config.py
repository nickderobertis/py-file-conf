from typing import Tuple, Optional, Type, Sequence, Any, Dict
import os
from copy import deepcopy

from pyfileconf.basemodels.file import ConfigFileBase
from pyfileconf.imports.models.statements.container import ImportStatementContainer
from pyfileconf.assignments.models.container import AssignmentStatementContainer

ImportsAndAssigns = Tuple[ImportStatementContainer, AssignmentStatementContainer]

class ConfigBase(dict):

    ##### Scaffolding functions or attributes. Need to override when subclassing  ####

    config_file_class = ConfigFileBase

    ##### Base class functions and attributes below. Shouldn't usually need to override in subclassing #####

    def __init__(self, d: dict=None, name: str=None, annotations: dict=None, imports: ImportStatementContainer = None,
                 _file: ConfigFileBase=None, begin_assignments: AssignmentStatementContainer=None,
                 klass: Optional[Type] = None, always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None,
                 **kwargs):
        if d is None:
            d = {}
        super().__init__(d, **kwargs)

        if annotations is None:
            annotations = {}

        if imports is None:
            imports = ImportStatementContainer([])

        if begin_assignments is None:
            begin_assignments = AssignmentStatementContainer([])

        self.name = name
        self.annotations = annotations
        self.imports = imports
        self._file = _file
        self.begin_assignments = begin_assignments
        self.klass = klass
        self.always_import_strs = always_import_strs
        self.always_assign_strs = always_assign_strs
        self._applied_updates: Dict[str, Any] = {}

    def __repr__(self):
        dict_repr = super().__repr__()
        class_name = self.__class__.__name__
        return f'<{class_name}(name={self.name}, {dict_repr})>'

    def __getattr__(self, attr):
        try:
            self[attr]
        except KeyError:
            raise AttributeError(attr)

    def __dir__(self):
        return self.keys()

    # argument names to match dict.update
    def update(self, E=None, pyfileconf_persist: bool = True, **F):  # type: ignore
        if E is None:
            E = {}

        # Track the updates so they can be applied later
        all_updates = {**E, **F}
        if pyfileconf_persist:
            self._applied_updates.update(all_updates)

        super().update(E, **F)

    def to_file(self, filepath: str):

        if self._file is None:
            output_file = self.config_file_class(
                filepath,
                name=self.name,
                klass=self.klass,
                always_import_strs=self.always_import_strs,
                always_assign_strs=self.always_assign_strs
            )
        else:
            # In case this is a new filepath for the same config, copy old file contents for use in new filepath
            output_file = deepcopy(self._file)
            output_file.filepath = filepath

        if os.path.exists(filepath):
            output_file.load() # load any existing config saved in the file, for preserving of user-saved inputs

        output_file.save(self)

    @classmethod
    def from_file(cls, filepath: str, name: str = None,
                  klass: Optional[Type] = None, always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None):
        file = cls.config_file_class(
            filepath,
            name=name,
            klass=klass,
            always_import_strs=always_import_strs,
            always_assign_strs=always_assign_strs
        )
        return file.load(cls)

    def as_imports_and_assignments(self) -> ImportsAndAssigns:
        assigns = AssignmentStatementContainer.from_dict_of_varnames_and_ast(self, self.annotations)

        return self.imports, self.begin_assignments + assigns

    def copy(self):
        return deepcopy(self)

    def _get_new_config_from_file(self):
        return self.__class__.from_file(
            self._file.filepath, name=self.name,
            klass=self.klass, always_import_strs=self.always_import_strs,
            always_assign_strs=self.always_assign_strs
        )

    def refresh(self) -> Dict[str, Any]:
        """
        Reloads from the existing, then re-applies any config updates. Useful for when
        this config depends on the attribute of some other config which was updated.
        :return: The updates made to the config
        """
        # Reload from file
        new_config = self._get_new_config_from_file()
        all_updates = {**new_config, **self._applied_updates}
        self.update(**all_updates, pyfileconf_persist=False)
        return all_updates

    def would_update(self, E=None, **F) -> bool:
        """
        Determines whether updates would actually cause
        a change in the config

        :param E: dictionary of updates
        :param F: kwargs of updates
        :return: whether config would actually change when calling .update with
            the same arguments
        """
        if E is None:
            E = {}

        all_updates = {**E, **F}
        for key, value in all_updates.items():
            if key not in self:
                continue
            orig_value = self[key]
            if orig_value != value:
                return True

        return False

    def change_from_refresh(self) -> Dict[str, Any]:
        """
        Determines whether refresh would actually cause
        a change in the config and returns a dictionary of
        what would be updated

        :return: the new config dict that would apply
            while calling .refresh if it would be updated,
            otherwise an empty dict
        """
        new_config = self._get_new_config_from_file()
        final_updates = {**new_config, **self._applied_updates}
        would_update = self.would_update(final_updates)
        if would_update:
            return final_updates
        return {}
