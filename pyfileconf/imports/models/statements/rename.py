from typing import TYPE_CHECKING, Sequence, cast

from pyfileconf.exceptions.imports import CouldNotExtractRenameException

if TYPE_CHECKING:
    from pyfileconf.imports.models.statements.interfaces import AnyAstImport
import ast

from mixins.repr import ReprMixin
from mixins.attrequals import EqOnAttrsMixin

class RenameStatement(ReprMixin, EqOnAttrsMixin):
    repr_cols = ['item', 'new_name']
    equal_attrs = ['item', 'new_name']

    def __init__(self, item: str, new_name: str):
        self.item = item
        self.new_name = new_name

    def __str__(self):
        return f'{self.item} as {self.new_name}'

    @classmethod
    def from_ast_alias(cls, alias: ast.alias):
        # Note: will fail if ast alias does not have a rename. See RenameStatementCollection.from_ast_import
        if alias.asname is None:
            raise CouldNotExtractRenameException(f'must pass alias which as .asname. passed alias: {alias}')

        return cls(
            alias.name,
            alias.asname
        )


class RenameStatementCollection(ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: Sequence[RenameStatement]):
        self.items = items

    def __contains__(self, item):
        if isinstance(item, RenameStatement):
            return item in self.items

        # If not rename statement, assuming got variable name
        return item in [rename_statement.item for rename_statement in self.items]

    def __getitem__(self, item):
        return self.item_map[item]

    def __iter__(self):
        for item in self.items:
            yield item

    @property
    def new_names(self):
        return [item.new_name for item in self]

    @property
    def orig_names(self):
        return [item.item for item in self]

    @property
    def item_map(self):
        return {rename_statement.item: rename_statement for rename_statement in self.items}

    @property
    def reverse_name_map(self):
        return {rename_statement.new_name: rename_statement.item for rename_statement in self.items}

    @property
    def name_map(self):
        return {rename_statement.item: rename_statement.new_name for rename_statement in self.items}

    @classmethod
    def from_ast_import(cls, ast_import: 'AnyAstImport'):
        # For ast aliases, they always exist whether the item is being renamed or not.
        # For RenameStatement objects, they only exist when there is a rename. Need to filter
        renames = []
        for alias in ast_import.names:
            alias = cast(ast.alias, alias)
            if alias.asname is not None:
                renames.append(RenameStatement.from_ast_alias(alias))

        return cls(renames)