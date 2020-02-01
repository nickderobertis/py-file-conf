from typing import Callable, Union, List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.pipelines.models.collection import PipelineCollection

from pyfileconf.basemodels.pipeline import Pipeline
from pyfileconf.views.object import ObjectView

PipelineOrFunction = Union[Pipeline, Callable]
PipelineOrFunctionOrCollection = Union[PipelineOrFunction, 'PipelineCollection']
PipelinesOrFunctions = List[PipelineOrFunction]
PipelinesOrFunctionsOrCollections = List[PipelineOrFunctionOrCollection]

# TODO [#27]: remove type ignores for recursive type definitions once mypy supports them
#
# See https://github.com/python/mypy/issues/731
PipelineDict = Dict[str, Union[PipelinesOrFunctions, 'PipelineDict']]  # type: ignore
PipelineDictOrPipelineOrFunction = Union[PipelineDict, PipelineOrFunction]  # type: ignore
PipelineDictsOrPipelinesOrFunctions = List[PipelineDictOrPipelineOrFunction]  # type: ignore

StrList = List[str]
ObjectViewOrCollection = Union[ObjectView, 'PipelineCollection']