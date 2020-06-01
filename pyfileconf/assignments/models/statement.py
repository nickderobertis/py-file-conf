from typing import Union, Tuple, Dict, Optional
import ast

from pyfileconf.exceptions.assignments import CouldNotExtractAssignmentFromAstException
from pyfileconf.io.file.write.asttosource import ast_node_to_source
from pyfileconf.io.file.load.parsers.assign import extract_assignment_from_ast
from mixins.repr import ReprMixin
from pyfileconf.mixins.orderpref import OrderPreferenceMixin

AnyAstAssign = Union[ast.Assign, ast.AnnAssign]

class AssignmentStatement(ReprMixin, OrderPreferenceMixin):
    repr_cols = ['varname', 'value', 'annotation']

    def __init__(self, target: ast.Name, value: ast.AST, annotation: ast.Name=None,
                 preferred_position: str = None):
        self.target = target
        self.varname = target.id if isinstance(target, ast.Name) else ast_node_to_source(target)  # handle subscripts, etc.
        self.value = value
        self.annotation = annotation
        self.preferred_position = preferred_position  # sets self.prefer_beginning as bool

        # Will get set to True if creating using classmethod self.from_str.
        # When set to True, will simply use the original str to output back to str
        self.created_from_str = False
        self.orig_str: Optional[str] = None

    def __str__(self):
        # Created from str, just return that str back (keeps whitespace, comments, etc.)
        if self.created_from_str:
            return self.orig_str

        # Not created from str, use ast to create str
        ast_assign = self.to_ast()
        return ast_node_to_source(ast_assign)

    def __eq__(self, other):
        if not isinstance(other, AssignmentStatement):
            # Auto convert ast assigns for comparison
            if isinstance(other, (ast.Assign, ast.AnnAssign)):
                other = AssignmentStatement.from_ast_assign(other)
            else:
                return False  # If not an assign or ast assign, not equal

        # Other is an assignment statement.
        if self.varname != other.varname:
            return False  # non-matching assignment variable, must not be equal

        # Other is an assignment statement to the same variable
        # Check if source generated from ast values are the same
        if ast_node_to_source(self.value) != ast_node_to_source(other.value):
            return False

        # Ignore differences on annotations. Could check that here.

        # Passed all checks, must be the same
        return True

    @classmethod
    def from_ast_assign(cls, ast_assign: AnyAstAssign, preferred_position: str = None):

        if isinstance(ast_assign, ast.Assign):
            # Base assignment, no annotation. May be multiple targets
            target = ast_assign.targets[0]

            # TODO [#1]: multiple assignments (multiple targets)
            if len(ast_assign.targets) > 1:
                raise NotImplementedError(f'cannot yet handle multiple assignment to: {ast_assign.targets}')

            annotation = None
        elif isinstance(ast_assign, ast.AnnAssign):
            # Annotation assignment. Must be single target.
            target = ast_assign.target
            annotation = ast_assign.annotation
        else:
            raise ValueError(f'expected ast.Assign or ast.AnnAssign. got {ast_assign} of type {type(ast_assign)}')

        # TODO [#22]: remove type ignores in AssignmentStatement.from_ast_assign once ast has proper type definitions
        return cls(
            target,  # type: ignore
            ast_assign.value,  # type: ignore
            annotation,  # type: ignore
            preferred_position=preferred_position
        )

    def to_default_dict_and_annotation_dict(self) -> Tuple[Dict[str, ast.AST], Dict[str, ast.Name]]:
        # Set default dict
        try:
            default_dict = {self.target.id: self.value}
        except AttributeError as e:
            if "no attribute 'id'" in str(e):
                try:
                    self.target.attr  # type: ignore
                    # Success, means that this was an attribute assignment like a.b = 6, do not need to put
                    # into default dict
                    default_dict = {}
                except AttributeError:
                    raise NotImplementedError(
                        f'do not understand how to parse {self.target} (dict: {self.target.__dict__})'
                    )
            else:
                raise e

        # Set annotation dict
        annotation_dict = {}
        if self.annotation is not None:
            annotation_dict = {self.target.id: self.annotation}

        return default_dict, annotation_dict

    def to_ast(self) -> AnyAstAssign:
        if self.annotation is None:
            return ast.Assign(
                targets=[self.target],
                value=self.value
            )
        else:
            return ast.AnnAssign(
                target=self.target,
                value=self.value,
                annotation=self.annotation,
                simple=1
            )

    @classmethod
    def from_varname_and_ast_value(cls, varname: str, value: ast.AST, annotation: ast.Name=None,
                                   preferred_position: str = None):
        assign_name = ast.Name(id=varname, ctx=ast.Store())

        return cls(assign_name, value=value, annotation=annotation, preferred_position=preferred_position)

    @classmethod
    def from_str(cls, assign_str: str, preferred_position: str = None):
        ast_module = ast.parse(assign_str)
        cls_obj = extract_assignment_from_ast(ast_module)
        if cls_obj is None:
            raise CouldNotExtractAssignmentFromAstException(f'Original str which created ast: {assign_str}')
        cls_obj.preferred_position = preferred_position
        cls_obj.created_from_str = True
        cls_obj.orig_str = assign_str

        return cls_obj