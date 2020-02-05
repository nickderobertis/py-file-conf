import ast
from typing import Tuple

from pyfileconf.io.func.load.args import FunctionArgsExtractor

class FunctionConfigExtractor(FunctionArgsExtractor):

    def extract_config(self, name: str=None):
        from pyfileconf.pipelines.models.config import FunctionConfig
        args, func_arg_imports = super().extract_args()

        # Parse into config
        defaults_dict, annotation_dict = function_args_as_arg_and_annotation_dict(args)

        return FunctionConfig(
            defaults_dict,
            annotations=annotation_dict,
            name=name,
            imports=func_arg_imports
        )



def function_args_as_arg_and_annotation_dict(args: ast.arguments) -> Tuple[dict, dict]:
    arg_dict = {}
    annotation_dict = {}

    # Handle args
    num_no_default_value = _get_length_of_arg_section(args.args) - _get_length_of_arg_section(args.defaults)
    all_defaults = [ast.NameConstant(value=None)] * num_no_default_value + _get_list_of_arg_section(args.defaults)
    assert len(all_defaults) == _get_length_of_arg_section(args.args)

    for i, arg in enumerate(args.args):
        default = all_defaults[i]
        arg_dict[arg.arg] = default
        if arg.annotation is not None:
            annotation_dict[arg.arg] = _strip_ast_quotes_if_necessary(arg.annotation)

    # Handle kwargs
    for i, kwarg in enumerate(args.kwonlyargs):
        default = args.kw_defaults[i]
        arg_dict[kwarg.arg] = default
        if kwarg.annotation is not None:
            annotation_dict[kwarg.arg] = _strip_ast_quotes_if_necessary(kwarg.annotation)

    return arg_dict, annotation_dict


def _get_length_of_arg_section(section):
    if section is None:
        return 0

    return len(section)


def _get_list_of_arg_section(section):
    if section is None:
        return []

    return list(section)


def _strip_ast_quotes_if_necessary(node: ast.AST) -> ast.AST:
    if isinstance(node, ast.Str):
        # Got a quoted annotation such as 'DataPipeline'. Strip the quotes
        str_value = node.s
        return ast.Name(str_value)
    return node
