from dero.manager.config.logic.load import get_user_defined_dict_from_module, load_file_as_module


class Config(dict):

    @classmethod
    def from_file(cls, filepath):
        module = load_file_as_module(filepath)
        config_dict = get_user_defined_dict_from_module(module)

        return cls(config_dict)



