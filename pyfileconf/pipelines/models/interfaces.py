from typing import Callable, Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.pipelines.models.collection import PipelineCollection

from pyfileconf.basemodels.pipeline import Pipeline
from pyfileconf.views.object import ObjectView

PipelineOrFunction = Union[Pipeline, Callable]
PipelineOrFunctionOrCollection = Union[PipelineOrFunction, 'PipelineCollection']
PipelinesOrFunctions = List[PipelineOrFunction]
PipelinesOrFunctionsOrCollections = List[PipelineOrFunctionOrCollection]
PipelineDict = Dict[str, Union[PipelinesOrFunctions, 'PipelineDict']]
PipelineDictOrPipelineOrFunction = Union[PipelineDict, PipelineOrFunction]
PipelineDictsOrPipelinesOrFunctions = List[PipelineDictOrPipelineOrFunction]
StrList = List[str]
ObjectViewOrCollection = Union[ObjectView, 'PipelineCollection']