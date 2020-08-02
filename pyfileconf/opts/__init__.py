"""
Options system for pyfileconf

To add a new option, the attribute and type hint to PyfileconfOptions,
add it to PyfileconfOptions.option_attrs,
add it to init and initialize it with the default,
and add a param docstring for it to PyfileconfOptionsManager.

Optionally, functions can be registered in PyfileconfOptions.option_callbacks
to perform an action upon setting or resetting the option. The callbacks
should accept the name of the option as the first argument and the value
being set as the second argument.
"""

from typing import Any, Tuple, Dict, Type, Iterable, List, Optional, Callable

from pyfileconf.logger.logger import logger
from pyfileconf.opts.filelog import add_file_handler_if_log_folder_exists_else_remove_handler


class PyfileconfOptions:
    log_stdout: bool
    log_folder: Optional[str]
    log_file_rollover_freq: str
    log_file_num_keep: int

    option_attrs: Tuple[str, ...] = (
        'log_stdout',
        'log_folder',
        'log_file_rollover_freq',
        'log_file_num_keep',
    )

    option_callbacks: Dict[str, Callable[[str, Any], None]] = {
        'log_folder': add_file_handler_if_log_folder_exists_else_remove_handler
    }

    def __init__(self, log_stdout: bool = False, log_folder: Optional[str] = None,
                 log_file_rollover_freq: str = 'D', log_file_num_keep: int = 0):
        self.log_stdout = log_stdout
        self.log_folder = log_folder
        self.log_file_rollover_freq = log_file_rollover_freq
        self.log_file_num_keep = log_file_num_keep

    def update(self, opts: 'PyfileconfOptions'):
        for attr in self.option_attrs:
            new_value = getattr(opts, attr)
            setattr(self, attr, new_value)


DEFAULT_OPTIONS = PyfileconfOptions()
options = PyfileconfOptions()


class PyfileconfOption:

    def __init__(self, name: str, callback: Optional[Callable[[str, Any], None]] = None):
        if callback is None:
            try:
                callback = PyfileconfOptions.option_callbacks[name]
            except KeyError:
                pass

        self.name = name
        self.callback = callback

    @property
    def value(self) -> Any:
        return getattr(options, self.name)

    @value.setter
    def value(self, val: Any):
        orig_value = getattr(options, self.name)
        setattr(options, self.name, val)
        if self.callback is not None and orig_value != val:
            self.callback(self.name, val)

    @property
    def default_value(self) -> Any:
        return getattr(DEFAULT_OPTIONS, self.name)

    def reset(self):
        logger.debug(f"Resetting option {self.name}")
        self.value = self.default_value

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

    :param log_stdout: Whether to capture stdout and log it in the
        pyfileconf logger
    :type log_stdout: bool
    :param log_folder: The folder in which logs should be stored
    :type log_folder: Optional[str]
    :param log_file_rollover_freq: How often to roll over to a new
        log file, see :py:class:`logging.handlers.TimedRotatingFileHandler`
        when option
    :param log_file_num_keep: Number of log files to keep, see
        :py:class:`logging.handlers.TimedRotatingFileHandler` backupCount option

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
        for attr in options.option_attrs:
            opt = getattr(self, attr)
            opt.reset()

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
