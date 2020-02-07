from typing import Optional, Sequence, Type

from mixins.repr import ReprMixin
from pyfileconf.basemodels.collection import Collection
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.logic.get import _get_from_nested_obj_by_section_path
from pyfileconf.imports.models.statements.container import ImportStatementContainer

class Registrar(ReprMixin):
    repr_cols = ['name', 'basepath', 'collection']
    collection_class = Collection

    def __init__(self, collection: Collection, basepath: str, name=None,
                 always_import_strs: Optional[Sequence[str]] = None,
                 always_assign_strs: Optional[Sequence[str]] = None, klass: Optional[Type] = None,
                 key_attr: str = 'name'):
        self.collection = collection
        self.basepath = basepath
        self.name = name

        self.always_import_strs = always_import_strs
        self.always_assign_strs = always_assign_strs
        self.klass = klass
        self.key_attr = key_attr

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
                  key_attr: str = 'name'):
        collection = cls.collection_class.from_dict(
            dict_, basepath=basepath, name=name, imports=imports,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr
        )

        return cls(
            collection, basepath=basepath, name=name,
            always_assign_strs=always_assign_strs, always_import_strs=always_import_strs, klass=klass,
            key_attr=key_attr
        )

    def scaffold_config(self):
        self.collection._output_config_files()

    def get(self, section_path_str: str):
        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final section or pipeline
        return _get_from_nested_obj_by_section_path(self, section_path)

    def to_nested_dict(self):
        return self.collection.to_nested_dict()
