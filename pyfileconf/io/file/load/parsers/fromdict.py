from typing import Union, cast
import ast

AstDict = Union[ast.Dict, ast.Call]

def extract_dict_from_ast_dict_or_dict_constructor(ast_dict: AstDict) -> dict:
    if isinstance(ast_dict, ast.Dict):
        return _extract_dict_from_ast_dict(ast_dict)
    elif isinstance(ast_dict, ast.Call):
        return _extract_dict_from_ast_dict_constructor(ast_dict)
    else:
        raise ValueError(f'expected ast.Dict or ast.Call, got {ast_dict} of type {type(ast_dict)}')

def _extract_dict_from_ast_dict(ast_dict: ast.Dict) -> dict:
    out_dict = {}
    for ast_key, ast_value in zip(ast_dict.keys, ast_dict.values):
        ast_key = cast(ast.Str, ast_key)
        # TODO [#25]: remove type ignores from _extract_dict_from_ast_dict when ast has better typing support
        key = ast_key.s  # type: ignore
        out_dict[key] = ast_value
    return out_dict

def _extract_dict_from_ast_dict_constructor(ast_dict: ast.Call) -> dict:
    from pyfileconf.io.file.load.parsers.kwargs import extract_keywords_from_ast
    ast_kwargs = extract_keywords_from_ast(ast_dict)
    return {key: ast_value for key, ast_value in ast_kwargs.items()}
