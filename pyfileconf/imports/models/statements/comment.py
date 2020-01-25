
from mixins.repr import ReprMixin

class Comment(ReprMixin):
    repr_cols = ['comment']

    def __init__(self, comment_str: str):
        self.comment = comment_str

    def __str__(self):
        return f'#{self.comment}'
