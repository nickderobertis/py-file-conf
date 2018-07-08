from typing import List

from dero.mixins.repr import ReprMixin
from dero.manager.basemodels.collection import Collection
from dero.manager.sectionpath.sectionpath import SectionPath
from dero.manager.logic.get import _get_from_nested_obj_by_section_path

class Registrar(ReprMixin):
    repr_cols = ['name', 'basepath', 'collection']
    collection_class = Collection

    def __init__(self, collection: Collection, basepath: str, name=None):
        self.collection = collection
        self.basepath = basepath
        self.name = name

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
                  loaded_modules: List[str]=None):
        collection = cls.collection_class.from_dict(
            dict_, basepath=basepath, name=name, loaded_modules=loaded_modules
        )

        return cls(collection, basepath=basepath, name=name)

    def scaffold_config(self):
        self.collection._output_config_files()

    def get(self, section_path_str: str):
        section_path = SectionPath(section_path_str)

        # Goes into nested sections, until it pulls the final section or pipeline
        return _get_from_nested_obj_by_section_path(self, section_path)