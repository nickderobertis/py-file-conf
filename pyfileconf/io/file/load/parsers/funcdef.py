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

    def visit_ClassDef(self, node):
        pass
        # don't go into children, so won't extract class methods


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

class FunctionDefinitionOrClassInitByNameExtractor(FunctionDefinitionByNameExtractor):

    def visit_ClassDef(self, node):
        if node.name == self.func_name:
            # Found a class definition matching the name we're looking for
            # Now look for the init method of that class
            # TODO [#11]: deal with subclassing where __init__ will not be in class definition
            orig_name = self.func_name
            self.func_name = '__init__'
            self.generic_visit(node)
            self.func_name = orig_name
            # Set back to looking for original name. Don't want to pull other inits

def extract_function_definitions_or_class_inits_from_ast_by_name(module: ast.AST, name: str) -> FunctionDefs:
    fe = FunctionDefinitionOrClassInitByNameExtractor(name)
    fe.visit(module)
    return fe.defs

def extract_function_definition_or_class_init_from_ast_by_name(module: ast.AST, name: str) -> FunctionDefOrNone:
    defs = extract_function_definitions_or_class_inits_from_ast_by_name(module, name)

    if len(defs) == 0:
        return None

    if len(defs) > 1:
        raise ValueError(f'found more than one function definition with the name {name} in module {module}')

    return defs[0]