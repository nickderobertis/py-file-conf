class Pipeline:

    def __init__(self):
        raise NotImplementedError("don't call Pipeline base class methods directly")

    def execute(self):
        raise NotImplementedError("don't call Pipeline base class methods directly")

    def new_instance_with_config(self, **kwargs):
        cls = self.__class__

        return cls(**kwargs)