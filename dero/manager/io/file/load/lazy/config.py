from typing import List

from dero.manager.io.file.load.lazy.base.impassign import ImportAssignmentLazyLoader
from dero.manager.config.logic.load import _split_lines_into_import_and_assignment

class ConfigFileLoader(ImportAssignmentLazyLoader):

    def load(self) -> dict:
        # Get ast, body, imports, assigns
        super().load()

        # Extract assignment portion of body
        self._file_body_to_assignment_body()

        # Parse assigns into config dict
        config_dict = self.assigns.to_dict()

        return config_dict

    @property
    def assignment_body(self) -> List[str]:
        return self._try_getattr_else_call_func('_assignment_body', self.load)

    def _file_body_to_assignment_body(self):
        """
        Warning: Assumes that imports come first, then an assignment section. May have
        issues when imports come later
        Returns:

        """
        import_lines, assignment_lines = _split_lines_into_import_and_assignment(self.body)
        self._assignment_body = assignment_lines

