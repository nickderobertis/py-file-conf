from typing import List

from dero.manager.basemodels.container import Container
from dero.manager.assignments.models.statement import AssignmentStatement

class AssignmentStatementContainer(Container):

    def __init__(self, items: List[AssignmentStatement]):
        self.items = items

    def to_dict(self):
        out_dict = {}
        for assign_statement in self.items:
            out_dict.update(
                assign_statement.to_dict()
            )

        return out_dict