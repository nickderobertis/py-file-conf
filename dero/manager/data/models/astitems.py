import ast

ast_none = ast.NameConstant(value=None)
ast_dict_constructor = ast.Call(
    func=ast.Name(id='dict'),
    args=[],
    keywords=[]
)

def ast_str(string: str) -> ast.Str:
    return ast.Str(s=string)

def ast_dict_constructor_with_kwargs_from_dict(d: dict) -> ast.Call:
    return ast.Call(
        func=ast.Name(id='dict'),
        args=[],
        keywords=[
            ast.keyword(
                arg=key,
                value=value
            ) for key, value in d.items()
        ]
    )