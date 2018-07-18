from copy import deepcopy

class Container:
    items = []

    def __iter__(self):
        for item in self.items:
            yield item

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items

    def __len__(self):
        return len(self.items)

    def append(self, item):
        self.items.append(item)

    def insert(self, index, item):
        self.items.insert(index, item)

    def copy(self):
        return deepcopy(self)

    def add_if_missing(self, item):
        """
        Checks if item is in container. If so, doesn't do anything.

        Assuming item is not in container,
        checks for prefer_beginning attribute of item. If True, insert at position 0.
        If False, or doesn't have attr, append to end.

        """
        add_to_begin = getattr(item, 'prefer_beginning', False)

        if add_to_begin:
            self.insert_if_missing(0, item)
        else:
            self.append_if_missing(item)

    def append_if_missing(self, item):
        if item not in self:
            self.append(item)

    def insert_if_missing(self, index, item):
        if item not in self:
            self.insert(index, item)

