from typing import Union, List
import ast

AstDictOrList = Union[ast.Dict, ast.List]
DictOrList = Union[dict, list]


class AstDictListConverter(ast.NodeVisitor):

    def __init__(self):
        self.collections = []

    def visit_Dict(self, node):
        self.collections.append(
            _ast_dict_to_dict(node)
        )
        # nested nodes being handled in function above

    def visit_List(self, node):
        self.collections.append(
            _ast_list_to_list(node)
        )
        # nested nodes being handled in function above

def extract_collections_from_ast(ast_node: ast.AST) -> List[DictOrList]:
    """
    returns a list of dicts or lists. Goes through ast, converting
    ast.Dict to dict and ast.List to list, leaving the rest intact.
    Returns a list of these created dicts and lists

    Args:
        ast_node:

    Returns:

    """
    adlc = AstDictListConverter()
    adlc.visit(ast_node)
    return adlc.collections


def _ast_dict_or_list_to_dict_or_list(node: AstDictOrList) -> DictOrList:
    if isinstance(node, ast.Dict):
        return _ast_dict_to_dict(node)
    elif isinstance(node, ast.List):
        return _ast_list_to_list(node)
    else:
        raise ValueError(f'expected ast.Dict or ast.List. Got {node} of type {type(node)}')


def _ast_dict_to_dict(ast_dict: ast.Dict) -> dict:
    out_dict = {}
    for key, value in zip(ast_dict.keys, ast_dict.values):
        key: ast.Str
        key_string = key.s
        if isinstance(value, (ast.Dict, ast.List)):
            store_value = _ast_dict_or_list_to_dict_or_list(value)
        else:
            store_value = value
        out_dict[key_string] = store_value

    return out_dict


def _ast_list_to_list(ast_list: ast.List) -> list:
    out_list = []
    for item in ast_list.elts:
        if isinstance(item, (ast.Dict, ast.List)):
            store_item = _ast_dict_or_list_to_dict_or_list(item)
        else:
            store_item = item
        out_list.append(store_item)

    return out_list