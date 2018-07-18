from typing import List, Tuple

from dero.manager.basemodels.container import Container
from dero.manager.assignments.models.statement import AssignmentStatement
from dero.mixins.repr import ReprMixin

class AssignmentStatementContainer(Container, ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: List[AssignmentStatement]):
        self.items = items

    def __str__(self):
        return '\n'.join(str(assign) for assign in self)

    def to_default_dict_and_annotation_dict(self) -> Tuple[dict, dict]:
        default_dict = {}
        annotation_dict = {}
        for assign_statement in self.items:
            default_item, annotation_item = assign_statement.to_default_dict_and_annotation_dict()
            default_dict.update(default_item)
            annotation_dict.update(annotation_item)

        return default_dict, annotation_dict

    @classmethod
    def from_dict_of_varnames_and_ast(cls, assignment_dict: dict, annotation_dict: dict=None,
                                      preferred_position: str = None):
        assigns = []
        for varname, value in assignment_dict.items():

            # Extract annotation if exists
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
