from typing import Union, List, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from pyfileconf.selector.models.itemview import ItemView

ListOfStrs = List[str]
StrOrListOfStrs = Union[str, ListOfStrs]
Result = Any
Results = List[Result]
ResultOrResults = Union[Result, Results]
StrOrView = Union[str, 'ItemView']
RunnerArgs = Union[str, List[str], 'ItemView', List['ItemView']]