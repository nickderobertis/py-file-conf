from typing import Any, Tuple, Dict, Type, Iterable, List

from pyfileconf.logger.logger import logger


class PyfileconfOptions:
    log_stdout: bool
    option_attrs: Tuple[str, ...] = (
        'log_stdout',
    )

    def __init__(self, log_stdout: bool = False):
        self.log_stdout = log_stdout

    def update(self, opts: 'PyfileconfOptions'):
        for attr in self.option_attrs:
            new_value = getattr(opts, attr)
            setattr(self, attr, new_value)


DEFAULT_OPTIONS = PyfileconfOptions()
options = PyfileconfOptions()


class PyfileconfOption:

    def __init__(self, name: str):
        self.name = name

    @property
    def value(self) -> Any:
        return getattr(options, self.name)

    @value.setter
    def value(self, val: Any):
        setattr(options, self.name, val)

    @property
    def default_value(self) -> Any:
        return getattr(DEFAULT_OPTIONS, self.name)

    def reset(self):
        logger.debug(f"Resetting option {self.name}")
        setattr(options, self.name, self.default_value)

    def __repr__(self):
        return f'<PyfileconfOption(name={self.name}, value={self.value}, ' \
               f'default_value={self.default_value})>'


class PyfileconfOptionsManager:
    """
    Allows setting options for the pyfileconf library

    :Usage:

    >>> import pyfileconf

    Use as a context manager with a single change:

    >>> with pyfileconf.options.set_option('log_stdout', True):
    >>>      # Do something
    >>> # Now options have been reset

    Use as a context manager with multiple individual changes:

    >>> with pyfileconf.options:
    >>>     # Change using set_option and the attribute name
    >>>     pyfileconf.options.set_option('log_stdout', True)
    >>>     # Change using option value attribute
    >>>     pyfileconf.options.log_stdout = True
    >>>     # More options changes, then desired operations
    >>> # Now options have been reset

    Use as a context manager with multiple changes at once:

    >>> with pyfileconf.options.set_options([('log_stdout', True), ('log_folder', 'MyLogs')]):
    >>>     # Operations needing options
    >>> # Now options have been reset

    Usage without context manager. The following three are equivalent to set options:

    >>> pyfileconf.options.set_option("log_stdout", True)
    >>> pyfileconf.options.set_options([("log_stdout", True)])
    >>> pyfileconf.options.log_stdout.value = True

    When using without the context manager, options will last until
    they are reset. Options can be reset individually, as a group,
    or all at once.

    >>> pyfileconf.options.log_stdout.reset()  # reset only the log_stdout option
    >>> pyfileconf.options.reset_option('log_stdout')  # reset only the log_stdout option
    # reset only the log_stdout option, but other options could be included
    >>> pyfileconf.options.reset_options(['log_stdout'])
    >>> pyfileconf.options.reset()  # reset all the options

    :Available Options:

    :param log_stdout: Boolean for whether to capture stdout and log it in the
        pyfileconf logger

    """
    def __init__(self):
        self._options: List[PyfileconfOption] = []
        for attr in options.option_attrs:
            opt = PyfileconfOption(attr)
            setattr(self, attr, opt)
            self._options.append(opt)

    def __repr__(self):
        opts_str = '\t' + '\n\t'.join(repr(opt) for opt in self._options) + '\n'
        return f'<PyfileconfOptionsManager(options=[\n{opts_str}])>'

    def __dir__(self) -> Iterable[str]:
        orig_items = super().__dir__()
        return list(orig_items) + list(options.option_attrs)

    def reset(self):
        """
        Undo all changes made through the options interface

        :return:
        """
        logger.debug(f"Resetting pyfileconf options")
        options.update(DEFAULT_OPTIONS)

    def set_option(self, attr: str, value: Any):
        """
        Set a particular option by its name

        :param attr: Option name
        :param value: New option value
        :return:
        """
        logger.debug(f"Setting option {attr} to {value}")
        opt: PyfileconfOption = getattr(self, attr)
        opt.value = value
        return self

    def set_options(self, updates: Iterable[Tuple[str, Any]]):
        """
        Set multiple options at once by their name
        :param updates: Multiple option updates
        :return:

        :Examples:

        >>> import pyfileconf
        >>> pyfileconf.options.set_options([('log_stdout', True), ('log_folder', 'MyLogs')])

        """
        for attr, value in updates:
            logger.debug(f"Setting option {attr} to {value}")
            opt: PyfileconfOption = getattr(self, attr)
            opt.value = value
        return self

    def reset_option(self, attr: str):
        """
        Reset a particular option by name

        :param attr: Name of option
        :return:
        """
        logger.debug(f'Resetting option {attr}')
        opt: PyfileconfOption = getattr(self, attr)
        opt.reset()

    def reset_options(self, attrs: Iterable[str]):
        """
        Reset multiple options at once by their names

        :param attrs: Option names
        :return:
        """
        for attr in attrs:
            self.reset_option(attr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reset()


options_interface = PyfileconfOptionsManager()
