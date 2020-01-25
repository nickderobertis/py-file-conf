from typing import List

class FileParser:

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> List[str]:
        with open(self.filepath, 'r', encoding='utf8') as f:
            contents = f.readlines()

        return contents