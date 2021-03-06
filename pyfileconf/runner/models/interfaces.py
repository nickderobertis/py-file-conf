from typing import Union, List, Any, TYPE_CHECKING, Tuple, Dict

if TYPE_CHECKING:
    from pyfileconf.selector.models.itemview import ItemView

ListOfStrs = List[str]
StrOrListOfStrs = Union[str, ListOfStrs]
Result = Any
Results = List[Result]
ResultOrResults = Union[Result, Results]
StrOrView = Union[str, "ItemView"]
RunnerArgs = Union[str, List[str], "ItemView", List["ItemView"]]
IterativeResult = Tuple[Tuple[Dict[str, Any], ...], Tuple[Any]]
IterativeResults = List[IterativeResult]