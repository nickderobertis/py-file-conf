from pyfileconf.io.file.load.lazy.dataast import SpecificClassDictAstLoader
from pyfileconf.io.file.load.parsers.collections import extract_collection_from_ast

class SpecificClassDictLoader(SpecificClassDictAstLoader):

    def load(self):
        # Get pipeline_dict_ast
        super().load()

        # Convert ast dicts and ast lists to normal dicts and lists, store as self.pipeline_dict
        self._class_dict_assign_to_dict()

        return self.class_dict

    @property
    def class_dict(self):
        return self._try_getattr_else_load('_class_dict')

    def _class_dict_assign_to_dict(self):
        """
        Iterates through ast tree of pipeline dict, producing a dict/list structure, while leaving
        other objects as ast representations

        Returns:

        """
        self._class_dict = extract_collection_from_ast(self.class_dict_assign.to_ast(), convert_str_values=True)
