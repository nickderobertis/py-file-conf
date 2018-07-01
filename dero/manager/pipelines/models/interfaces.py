from typing import Callable, Union, List, Dict

from dero.manager.pipelines.models.pipeline import Pipeline

PipelineOrFunction = Union[Pipeline, Callable]
PipelineOrFunctionOrCollection = Union[PipelineOrFunction, 'PipelineCollection']
PipelinesOrFunctions = List[PipelineOrFunction]
PipelinesOrFunctionsOrCollections = List[PipelineOrFunctionOrCollection]
PipelineDict = Dict[str, Union[PipelinesOrFunctions, 'PipelineDict']]
PipelineDictOrPipelineOrFunction = Union[PipelineDict, PipelineOrFunction]
PipelineDictsOrPipelinesOrFunctions = List[PipelineDictOrPipelineOrFunction]
StrList = List[str]