import ast
from typing import List, Optional


class NameExtractor(ast.NodeVisitor):

    def __init__(self):
        self.names = []

    def visit_Name(self, node):
        self.names.append(node.id)


def extract_external_name_from_assign_value(ast_node: ast.AST) -> Optional[str]:
    """
    Identifies the root part of an assignment value, so long as it is not builtin.

    Examples
    from a import b

    b -> 'b'
    b.attr -> 'b'

    import c

    c.test -> 'c'
    c.thing.stuff -> 'c'

    'abc' -> None
    123 -> None

    Args:
        ast_node: should be ast form of the value of an assignment

    Returns:

    """
    ne = NameExtractor()
    ne.visit(ast_node)

    if len(ne.names) == 0:
        return None

    if len(ne.names) > 1:
        raise ValueError(f'expected single name, got {ne.names}')

    return ne.names[0]


def extract_unique_external_names_from_assign_value(ast_node: ast.AST) -> List[str]:
    """
    Same as extract_external_name_from_assign_value but returns a list always, can return multiple names,
    and drops duplicates in the returned names
    """
    ne = NameExtractor()
    ne.visit(ast_node)

    return list(set(ne.names))
