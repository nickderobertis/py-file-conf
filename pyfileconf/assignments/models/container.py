import ast
from typing import List, Tuple, Dict, Optional

from pyfileconf.basemodels.container import Container
from pyfileconf.assignments.models.statement import AssignmentStatement
from mixins.repr import ReprMixin

class AssignmentStatementContainer(Container, ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: List[AssignmentStatement]):
        self.items = items

    def __str__(self):
        return ''.join(str(assign) for assign in self)

    def contains_varname(self, varname: str):
        return any([assign.varname == varname for assign in self])

    def to_default_dict_and_annotation_dict(self) -> Tuple[Dict[str, ast.AST], Dict[str, ast.Name]]:
        default_dict: Dict[str, ast.AST] = {}
        annotation_dict: Dict[str, ast.Name] = {}
        for assign_statement in self.items:
            default_item, annotation_item = assign_statement.to_default_dict_and_annotation_dict()
            default_dict.update(default_item)
            annotation_dict.update(annotation_item)

        return default_dict, annotation_dict

    @classmethod
    def from_dict_of_varnames_and_ast(cls, assignment_dict: Dict[str, ast.AST],
                                      annotation_dict: Dict[str, ast.Name] = None,
                                      preferred_position: str = None):
        if annotation_dict is None:
            annotation_dict = {}

        assigns = []
        for varname, value in assignment_dict.items():

            # Extract annotation if exists
            annotation: Optional[ast.Name]
            if varname in annotation_dict:
                annotation = annotation_dict[varname]
            else:
                annotation = None

            # Create assignment statement
            assigns.append(
                AssignmentStatement.from_varname_and_ast_value(
                    varname,
                    value=value,
                    annotation=annotation,
                    preferred_position=preferred_position
                )
            )

        return cls(assigns)
