from typing import List

from dero.manager.basemodels.container import Container
from dero.manager.assignments.models.statement import AssignmentStatement

class AssignmentStatementContainer(Container):

    def __init__(self, items: List[AssignmentStatement]):
        self.items = items