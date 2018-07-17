import ast

from dero.manager.io.file.load.parsers.base import FileParser

class PythonFileParser(FileParser):

    def load(self) -> ast.Module:
        # Get text of file
        file_str = super().load()

        # Parse into ast
        module: ast.Module = ast.parse(file_str)

        return module