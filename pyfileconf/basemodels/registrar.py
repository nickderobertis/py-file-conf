import os
from typing import Optional, Sequence, Type, Any

from mixins.repr import ReprMixin
from pyfileconf.basemodels.collection import Collection
from pyfileconf.logic.set import _set_in_nested_obj_by_section_path
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.logic.get import _get_from_nested_obj_by_section_path
from pyfileconf.imports.models.statements.container import ImportStatementContainer

class Registrar(ReprMixin):
    repr_cols = ['name', 'basepath', 'collection']
    collection_class = Collection

    def __init__(self, collection: Collection, basepath: str, name=None,
                 always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                 key_attr: str = 'name', execute_attr: str = '__call__'):
        self.collection = collection
        self.basepath = basepath
        self.name = name

        self.always_import_strs = always_import_strs
        self.always_assign_strs = always_assign_strs
        self.klass = klass
        self.key_attr = key_attr
        self.execute_attr = execute_attr

    def __getattr__(self, item):
        return getattr(self.collection, item)

    def __dir__(self):
        exposed_methods = [
            'scaffold_config',
            'get'
        ]
        exposed_attrs = [
            'basepath',
            'name'
        ]
        collection_attrs = [attr for attr in dir(self.collection) if attr not in exposed_methods + exposed_attrs]
        return exposed_methods + exposed_attrs + collection_attrs

    @classmethod
    def from_dict(cls, dict_: dict, basepath: str, name: str=None,
                  imports: ImportStatementContainer = None, always_import_strs: Optional[Sequence[str]] = None,
                  always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                  key_attr: str = 'name', execute_attr: str = '__call__'):
        collection = cls.collection_class.from_dict(
            dict_, basepath=basepath, name=name, imports=imports,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr, execute_attr=execute_attr
        )

        return cls(
            collection, basepath=basepath, name=name,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr, execute_attr=execute_attr
        )

    def scaffold_config(self):
        self.collection._output_config_files()

    def scaffold_config_for(self, section_path_str: str):
        section_path = SectionPath(section_path_str)

        collection = _get_from_nested_obj_by_section_path(self, section_path[:-1])
        collection._output_config_files()

    def get(self, section_path_str: str):
        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final section or pipeline
        return _get_from_nested_obj_by_section_path(self, section_path)

    def set(self, section_path_str: str, value: Any):
        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it sets the final section or pipeline
        obj = self
        section_basepath = self.basepath
        for i, section in enumerate(section_path):
            section_basepath = os.path.join(section_basepath, section)
            try:
                obj = getattr(obj, section)
            except AttributeError as e:
                new_collection = self.collection_class(
                    section_basepath, [], name=section, imports=self.imports,
                    always_assign_strs=self.always_assign_strs,
                    always_import_strs=self.always_import_strs, klass=self.klass,
                    key_attr=self.key_attr, execute_attr=self.execute_attr
                )
                obj.append(new_collection)
                obj = getattr(obj, section)

        # Now have collection object which should hold this final object
        obj.append(value)

    def to_nested_dict(self):
        return self.collection.to_nested_dict()
