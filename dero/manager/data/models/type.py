


class DataType:

    def __init__(self, name=None):
        self.name = name

    def __add__(self, other):
        return self.name + other

    def __radd__(self, other):
        return other + self.name

    def __repr__(self):
        return f'<DataType({self.name})>'