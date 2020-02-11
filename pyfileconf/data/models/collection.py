from copy import deepcopy
from typing import Union, cast, Any, Type
import os

from pyfileconf.basemodels.collection import Collection
from pyfileconf.data.logic.convert import convert_to_empty_obj_if_necessary
from pyfileconf.logic.get import _get_public_name_or_special_name
from pyfileconf.data.models.config import SpecificClassConfig
from pyfileconf.io.func.load.args import extract_function_args_and_arg_imports_from_import
from pyfileconf.imports.models.statements.obj import ObjectImportStatement
from pyfileconf.imports.logic.load.name import get_module_and_name_imported_from
from pyfileconf.data.models.astitems import ast_str
from pyfileconf.io.func.load.config import function_args_as_arg_and_annotation_dict


ObjOrCollection = Union[Any, 'SpecificClassCollection']

class SpecificClassCollection(Collection):
    klass: Type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.klass is None:
            raise ValueError('must pass class for SpecificClassCollection')

    def _set_name_map(self) -> None:
        obj_map = {}
        for obj_or_collection in self:
            obj_or_collection = cast(ObjOrCollection, obj_or_collection)
            if isinstance(obj_or_collection, SpecificClassCollection):
                key_attr = 'name'
            else:
                key_attr = self.key_attr
            obj_name = getattr(obj_or_collection, key_attr)
            obj_map[obj_name] = obj_or_collection
        self.name_dict = obj_map

    def _transform_item(self, item):
        """
        Is called on each item when adding items to collection. Should handle whether the item
        is an actual item or another collection. Must return the item or collection.

        If not overridden, will just store items as is.

        Returns: item or Collection

        """
        return convert_to_empty_obj_if_necessary(item, self.klass, key_attr=self.key_attr)

    def _output_config_files(self) -> None:
        if not os.path.exists(self.basepath):
            os.makedirs(self.basepath)

        for item in self:
            self._output_config_file(item)

    def _output_config_file(self, item: ObjOrCollection) -> None:
        if isinstance(item, SpecificClassCollection):
            # if collection, recursively call creating config files
            return item._output_config_files()

        # Dealing with object itself
        item_name = getattr(item, self.key_attr)
        item_filepath = os.path.join(self.basepath, item_name + '.py')

        class_config = dict(
            klass=self.klass,
            always_import_strs=self.always_import_strs,
            always_assign_strs=self.always_assign_strs
        )

        if os.path.exists(item_filepath):
            file_existed = True
            # if config file already exists, load confguration from file, use to update file defaults
            existing_config = SpecificClassConfig.from_file(
                item_filepath,
                name=item_name,
                **class_config,  # type: ignore
            )
            existing_imports = existing_config._file.interface.imports
            # Here using the ast config, for the purpose of writing to file
            file_config_item = deepcopy(item)
            apply_config(file_config_item, existing_config)
            # also use to update DataSource object in memory. Here use the actual objects instead of ast
            apply_config(item, existing_config.active_config_dict)
        else:
            file_existed = False
            existing_imports = None
            file_config_item = item

        item_config = SpecificClassConfig(imports=existing_imports,
                                                   file_path=item_filepath,
                                                   **class_config)  # type: ignore

        # Get config by extracting from class __init__
        # First need to create dummy import for compatibility
        mod, import_base = get_module_and_name_imported_from(self.klass)
        obj_import = ObjectImportStatement([item_name], import_base)
        # Now get the arguments and the imports for any type annotations
        args, func_arg_imports = extract_function_args_and_arg_imports_from_import(
            self.klass.__name__,
            obj_import
        )
        # Convert into a usable formats:
        # defaults_dict: a dictionary where keys are variable names and values are ast defaults
        # annotation_dict: a dicrionary where keys are variable names and values are ast type annotations
        defaults_dict, annotation_dict = function_args_as_arg_and_annotation_dict(args)
        defaults_dict[self.key_attr] = ast_str(item_name)  # set name attribute as item name by default
        # Apply all the new extracted defaults to the created config
        item_config.update(defaults_dict)
        item_config.annotations.update(annotation_dict)
        item_config.imports.extend(func_arg_imports)

        item_config.to_file(item_filepath)

        if not file_existed:
            # If this was a new output, we now need to load again to get the object representation
            # instead of just the ast representation
            existing_config = SpecificClassConfig.from_file(item_filepath, item_name, **class_config)  # type: ignore
            apply_config(item, existing_config.active_config_dict)


def apply_config(obj: Any, config: 'SpecificClassConfig') -> None:
    attributes = dir(obj)
    for config_attr, config_item in config.items():
        # Skip irrelevant items
        if config_attr in attributes:
            setattr(obj, config_attr, config_item)