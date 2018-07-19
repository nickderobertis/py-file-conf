


class DataType:

    def __init__(self, name=None):
        self.name = name

    def __add__(self, other):
        return self.name + other

    def __radd__(self, other):
        return other + self.name

    def __repr__(self):
        return f'<DataType({self.name})>'

    def __eq__(self, other):
        # Handle when other is None
        if other is None:
            if self.name is None:
                return True
            else:
                return False

        # Handle when other is str
        if isinstance(other, str):
            return self.name == other

        # Handle when other is DataType
        return self.name == other.name