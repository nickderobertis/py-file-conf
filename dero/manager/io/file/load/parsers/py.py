import ast

from dero.manager.io.file.load.parsers.base import FileParser

class PythonFileParser(FileParser):

    def load(self) -> ast.AST:
        # Get text of file
        file_str = super().load()

        # Parse into ast