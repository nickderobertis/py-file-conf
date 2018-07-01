import sys

class ImportTracker:

    def __init__(self):
        self.original_modules = list(sys.modules.keys())

    @property
    def imported_modules(self):
        current_modules = list(sys.modules.keys())
        return [module for module in current_modules if module not in self.original_modules]

