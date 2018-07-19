import ast
import astor

def ast_node_to_source(ast_node: ast.AST) -> str:
    """
    Uses astor package to produce source code from ast

    Also handles low-level ast functions, such as wrapping in a module if necessary,
    and fixing line numbers for modified/extracted ast

    Args:
        ast_node:

    Returns:

    """

    # Must be a module to output to source. Wrap in module if not already
    if not isinstance(ast_node, ast.Module):
        ast_node = ast.Module([ast_node])

    # Fix line numbers
    ast.fix_missing_locations(ast_node)

    return astor.to_source(ast_node)