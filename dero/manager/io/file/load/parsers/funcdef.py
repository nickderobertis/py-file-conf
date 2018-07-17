import ast
from typing import List, Union

FunctionDefOrNone = Union[ast.FunctionDef, None]
FunctionDefs = List[ast.FunctionDef]

class FunctionDefinitionExtractor(ast.NodeVisitor):

    def __init__(self):
        self.defs = []

    def visit_FunctionDef(self, node):
        self.defs.append(node)
        # don't go into children, so won't extract nested functions


def extract_function_definitions_from_ast(module: ast.AST) -> FunctionDefs:
    fe = FunctionDefinitionExtractor()
    fe.visit(module)
    return fe.defs

class FunctionDefinitionByNameExtractor(FunctionDefinitionExtractor):

    def __init__(self, func_name: str):
        self.func_name = func_name
        super().__init__()

    def visit_FunctionDef(self, node):
        if node.name == self.func_name:
            super().visit_FunctionDef(node)

def extract_function_definitions_from_ast_by_name(module: ast.AST, name: str) -> FunctionDefs:
    fe = FunctionDefinitionByNameExtractor(name)
    fe.visit(module)
    return fe.defs

def extract_function_definition_from_ast_by_name(module: ast.AST, name: str) -> FunctionDefOrNone:
    defs = extract_function_definitions_from_ast_by_name(module, name)

    if len(defs) == 0:
        return None

    if len(defs) > 1:
        raise ValueError(f'found more than one function definition with the name {name} in module {module}')

    return defs[0]