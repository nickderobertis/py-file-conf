from typing import Callable, Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.pipelines.models.collection import PipelineCollection

from pyfileconf.views.object import ObjectView

FunctionOrCollection = Union[Callable, 'PipelineCollection']

StrList = List[str]
ObjectViewOrCollection = Union[ObjectView, 'PipelineCollection']