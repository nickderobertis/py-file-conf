class PyfileconfBase:
    """
    A base class which can be used to autocomplete
    the possible custom methods which modify
    how pyfileconf works with the object.

    It is not necessary to use this base class, instead the
    methods can be defined on any class.
    """

    def _pyfileconf_update_(self, **kwargs) -> None:
        """
        Called to apply configuration to the object. If this method
        is not defined on the class, __init__ will be used instead.

        :param kwargs: key/value pairs where keys are name of config
            attributes and values are the config values
        :return: None
        """
        self.__init__(**kwargs)  # type: ignore
