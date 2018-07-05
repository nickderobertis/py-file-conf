from typing import List

from dero.mixins.repr import ReprMixin
from dero.mixins.attrequals import EqOnAttrsMixin
from dero.manager.imports.logic.parse.patterns import re_patterns

class RenameStatement(ReprMixin, EqOnAttrsMixin):
    repr_cols = ['item', 'new_name']
    equal_attrs = ['item', 'new_name']

    def __init__(self, item: str, new_name: str):
        self.item = item
        self.new_name = new_name

    def __str__(self):
        return f'{self.item} as {self.new_name}'

    @classmethod
    def from_str(cls, rename_str: str):
        pattern = re_patterns['rename parts']
        match = pattern.fullmatch(rename_str)

        if match is None:
            raise ValueError(f'could not parse rename statement {rename_str}')

        item, new_name = match.groups()

        obj = cls(item=item, new_name=new_name)
        obj._orig_str = rename_str

        return obj


class RenameStatementCollection(ReprMixin):
    repr_cols = ['items']

    def __init__(self, items: [RenameStatement]):
        self.items = items

    def __contains__(self, item):
        return item in [rename_statement.item for rename_statement in self.items]

    def __getitem__(self, item):
        return self.item_map[item]

    def __iter__(self):
        for item in self.items:
            yield item

    @property
    def item_map(self):
        return {rename_statement.item: rename_statement for rename_statement in self.items}

    @classmethod
    def from_str_list(cls, rename_strs: List[str]):
        return cls([RenameStatement.from_str(rename_str) for rename_str in rename_strs])