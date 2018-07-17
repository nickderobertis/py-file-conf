

class FileParser:

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> str:
        with open(self.filepath, 'r') as f:
            contents = f.read()

        return contents