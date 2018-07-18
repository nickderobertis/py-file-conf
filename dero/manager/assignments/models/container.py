from typing import List

from dero.manager.basemodels.container import Container
from dero.manager.assignments.models.statement import AssignmentStatement

class AssignmentStatementContainer(Container):

    def __init__(self, items: List[AssignmentStatement]):
        self.items = items

    def __str__(self):
        return '\n'.join(str(assign) for assign in self)

    def to_dict(self):
        out_dict = {}
        for assign_statement in self.items:
            out_dict.update(
                assign_statement.to_dict()
            )

        return out_dict

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
