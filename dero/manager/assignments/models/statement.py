from typing import Union
import ast

AnyAstAssign = Union[ast.Assign, ast.AnnAssign]

class AssignmentStatement:


    def __init__(self, target: ast.Name, value: ast.AST, annotation: ast.Name=None):
        self.target = target
        self.value = value
        self.annotation = annotation

    @classmethod
    def from_ast_assign(cls, ast_assign: AnyAstAssign):

        if isinstance(ast_assign, ast.Assign):
            # Base assignment, no annotation. May be multiple targets
            target = ast_assign.targets[0]

            # TODO: multiple assignments (multiple targets)
            if len(ast_assign.targets) > 1:
                raise NotImplementedError(f'cannot yet handle multiple assignment to: {ast_assign.targets}')

            annotation = None
        elif isinstance(ast_assign, ast.AnnAssign):
            # Annotation assignment. Must be single target.
            target = ast_assign.target
            annotation = ast_assign.annotation
        else:
            raise ValueError(f'expected ast.Assign or ast.AnnAssign. got {ast_assign} of type {type(ast_assign)}')

        return cls(
            target,
            ast_assign.value,
            annotation
        )
