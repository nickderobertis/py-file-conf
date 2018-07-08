from typing import Callable, Any, List
import inspect

from dero.manager.basemodels.config import ConfigBase
from dero.manager.imports.logic.load.func import function_args_as_dict
from dero.manager.pipelines.models.interfaces import PipelineOrFunction
from dero.manager.basemodels.pipeline import Pipeline
from dero.manager.logic.get import _get_public_name_or_special_name
from dero.manager.config.models.file import FunctionConfigFile

class FunctionConfig(ConfigBase):

    config_file_class = FunctionConfigFile

    def for_function(self, func: Callable) -> dict:
        """
        Strips out items of config which are not applicable to function. Returns dictionary
        of config items for passing to the function.

        Args:
            func: func for which to filter out config items

        Returns: dict, applicable config for func
        """
        # Only pass items in config which are arguments of function
        func_kwargs = function_args_as_dict(func)
        return {key: value for key, value in self.items() if key in func_kwargs}

    @classmethod
    def from_function(cls, func: Callable, name: str=None, loaded_modules: List[str]=None):
        config_dict = function_args_as_dict(func)
        if name is None:
            name = _get_public_name_or_special_name(func)

        return cls(config_dict, name=name, _loaded_modules=loaded_modules)

    @classmethod
    def from_pipeline(cls, item: PipelineOrFunction, name: str=None, loaded_modules: List[str]=None):
        init_func = _pipeline_class_or_instance_or_method_to_init_func(item)
        if name is None:
            name = _get_public_name_or_special_name(item)
        return cls.from_function(init_func, name=name, loaded_modules=loaded_modules)

    @classmethod
    def from_pipeline_or_function(cls, item: PipelineOrFunction, name: str=None, loaded_modules: List[str]=None):
        func = _function_or_pipeline_to_function(item)
        if name is None:
            name = _get_public_name_or_special_name(item)
        return cls.from_function(func, name=name, loaded_modules=loaded_modules)


def _function_or_pipeline_to_function(obj_or_class: Any) -> Callable:
    if _is_pipeline_instance_or_pipeline_class(obj_or_class) or _is_pipeline_method(obj_or_class):
        return _pipeline_class_or_instance_or_method_to_init_func(obj_or_class)

    # must be function separate from pipeline
    return obj_or_class

def _pipeline_class_or_instance_or_method_to_init_func(obj_or_class: Any) -> Callable:
    if _is_pipeline_instance_or_pipeline_class(obj_or_class):
        # Got Pipeline instance, or Pipeline class
        return obj_or_class.__init__
    if isinstance(obj_or_class, Callable):
        # Got method of pipeline class. Pull object, then pull init method
        return obj_or_class.__self__.__init__


def _is_pipeline_instance_or_pipeline_class(obj_or_class: Any) -> bool:
    return isinstance(obj_or_class, Pipeline) or (inspect.isclass(obj_or_class) and issubclass(obj_or_class, Pipeline))

def _is_pipeline_method(obj_or_class: Any) -> bool:
    if not _is_class_method(obj_or_class):
        return False

    # Must be a class method. Determine if is pipeline class
    obj = obj_or_class.__self__
    if isinstance(obj, Pipeline):
        return True

    return False

def _is_class_method(obj_or_class: Any) -> bool:
    if not isinstance(obj_or_class, Callable):
        # not a function, can't be a method
        return False

    if not hasattr(obj_or_class, '__self__'):
        # not a class method, standalone function
        return False

    return True