from typing import Tuple, Optional, Type, Sequence
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
    def update(self, E=None, **F):
        if E is None:
            E = {}
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