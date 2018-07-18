from typing import List, Tuple
import os
from copy import deepcopy

from dero.manager.basemodels.file import ConfigFileBase
from dero.manager.imports.models.statements.container import ImportStatementContainer
from dero.manager.assignments.models.container import AssignmentStatementContainer

ImportsAndAssigns = Tuple[ImportStatementContainer, AssignmentStatementContainer]

class ConfigBase(dict):

    ##### Scaffolding functions or attributes. Need to override when subclassing  ####

    config_file_class = ConfigFileBase

    ##### Base class functions and attributes below. Shouldn't usually need to override in subclassing #####

    def __init__(self, d: dict=None, name: str=None, annotations: dict=None, imports: ImportStatementContainer = None,
                 _file: ConfigFileBase=None, **kwargs):
        if d is None:
            d = {}
        super().__init__(d, **kwargs)
        self.name = name
        self.annotations = annotations
        self.imports = imports
        self._file = _file

    def __repr__(self):
        dict_repr = super().__repr__()
        class_name = self.__class__.__name__
        return f'<{class_name}(name={self.name}, {dict_repr})>'

    def __getattr__(self, attr):
        return self[attr]

    def __dir__(self):
        return self.keys()

    def update(self, d: dict=None, **kwargs):
        if d is None:
            d = {}
        super().update(d, **kwargs)

    def to_file(self, filepath: str):

        if self._file is None:
            output_file = self.config_file_class(filepath, name=self.name, loaded_modules=self._loaded_modules)
        else:
            # In case this is a new filepath for the same config, copy old file contents for use in new filepath
            output_file = deepcopy(self._file)
            output_file.filepath = filepath

        if os.path.exists(filepath):
            output_file.load() # load any existing config saved in the file, for preserving of user-saved inputs

        output_file.save(self)

    @classmethod
    def from_file(cls, filepath: str, name: str = None):
        file = cls.config_file_class(filepath, name=name)
        return file.load()

    def as_imports_and_assignments(self) -> ImportsAndAssigns:
        assigns = AssignmentStatementContainer.from_dict_of_varnames_and_ast(self, self.annotations)

        return self.imports, assigns