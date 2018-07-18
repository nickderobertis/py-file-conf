import ast

class KeywordExtractor(ast.NodeVisitor):

    def __init__(self):
        self.kwargs = {}

    def visit_keyword(self, node):
        self.kwargs[node.arg] = node.value
        self.generic_visit(node)


def extract_keywords_from_ast(node: ast.AST) -> dict:
    ke = KeywordExtractor()
    ke.visit(node)
    return ke.kwargs


class KeywordByNameExtractor(KeywordExtractor):

    def __init__(self, name: str):
        self.name = name
        super().__init__()

    def visit_keyword(self, node):
        if node.arg == self.name:
            super().visit_keyword(node)


def extract_keywords_from_ast_by_name(node: ast.AST, name: str) -> dict:
    ke = KeywordByNameExtractor(name)
    ke.visit(node)
    return ke.kwargs