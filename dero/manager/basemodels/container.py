

class Container:
    items = []

    def __iter__(self):
        for item in self.items:
            yield item

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items

    def append(self, item):
        self.items.append(item)

    def insert(self, index, item):
        self.items.insert(index, item)