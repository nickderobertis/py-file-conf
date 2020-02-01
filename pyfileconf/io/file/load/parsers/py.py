from typing import Tuple, List
import ast

from pyfileconf.io.file.load.parsers.base import FileParser

AstModuleAndStrListTuple = Tuple[ast.Module, List[str]]

class PythonFileParser(FileParser):

    def load(self) -> AstModuleAndStrListTuple:  # type: ignore
        # Get text of file
        file_lines = super().load()

        # Parse into ast
        module: ast.Module = ast.parse(''.join(file_lines))

        return module, file_lines