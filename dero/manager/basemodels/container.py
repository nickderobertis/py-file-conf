

class Container:
    items = []

    def __iter__(self):
        for item in self.items:
            yield item

    def __getitem__(self, item):
        return self.items[item]

    def __contains__(self, item):
        return item in self.items