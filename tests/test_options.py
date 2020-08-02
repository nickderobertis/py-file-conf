import logging
import os
from typing import Any, Tuple

import pyfileconf
from pyfileconf import Selector, PipelineManager
from pyfileconf.logger.logger import logger
from pyfileconf.opts import options
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.selector.models.itemview import ItemView

from tests.test_pipeline_manager.base import PipelineManagerTestBase


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


class OptionsTest(PipelineManagerTestBase):
    pass

class TestOptionsModify(OptionsTest):

    def test_modify_option_by_setting_value(self):
        assert not options.log_stdout
        pyfileconf.options.log_stdout.value = True
        assert options.log_stdout
        pyfileconf.options.log_stdout.value = False
        assert not options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout
        pyfileconf.options.log_stdout.value = True
        assert options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout
        pyfileconf.options.log_stdout.value = True
        assert options.log_stdout
        pyfileconf.options.log_stdout.reset()
        assert not options.log_stdout
        pyfileconf.options.log_stdout.value = True
        assert options.log_stdout
        pyfileconf.options.reset_option('log_stdout')
        assert not options.log_stdout
        pyfileconf.options.log_stdout.value = True
        assert options.log_stdout
        pyfileconf.options.reset_options(['log_stdout'])
        assert not options.log_stdout

    def test_modify_option_by_setting_value_in_context_manager(self):
        assert not options.log_stdout
        with pyfileconf.options:
            pyfileconf.options.log_stdout.value = True
            assert options.log_stdout
        assert not options.log_stdout
        with pyfileconf.options:
            pyfileconf.options.log_stdout.value = False
            assert not options.log_stdout
        assert not options.log_stdout

    def test_modify_option_by_set_option(self):
        assert not options.log_stdout
        pyfileconf.options.set_option('log_stdout', True)
        assert options.log_stdout
        pyfileconf.options.set_option('log_stdout', False)
        assert not options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout
        pyfileconf.options.set_option('log_stdout', True)
        assert options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout

    def test_modify_option_by_set_options(self):
        assert not options.log_stdout
        pyfileconf.options.set_options([('log_stdout', True)])
        assert options.log_stdout
        pyfileconf.options.set_options([('log_stdout', False)])
        assert not options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout
        pyfileconf.options.set_options([('log_stdout', True)])
        assert options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout

    def test_modify_option_by_set_option_context_manager(self):
        assert not options.log_stdout
        with pyfileconf.options.set_option('log_stdout', True):
            assert options.log_stdout
        assert not options.log_stdout
        with pyfileconf.options.set_option('log_stdout', False):
            assert not options.log_stdout
        assert not options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout

    def test_modify_option_by_set_options_context_manager(self):
        assert not options.log_stdout
        with pyfileconf.options.set_options([('log_stdout', True)]):
            assert options.log_stdout
        assert not options.log_stdout
        with pyfileconf.options.set_options([('log_stdout', False)]):
            assert not options.log_stdout
        assert not options.log_stdout
        pyfileconf.options.reset()
        assert not options.log_stdout


class TestLogOptions(OptionsTest):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.mock_logs = MockLoggingHandler()
        logger.addHandler(cls.mock_logs)

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        logger.handlers = [h for h in logger.handlers if not isinstance(h, MockLoggingHandler)]

    def teardown_method(self, method):
        super().teardown_method(method)
        self.mock_logs.reset()

    def create_pm_with_function_and_run(self) -> Tuple[PipelineManager, ItemView, Any]:
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm(include_logs=False)
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        return pipeline_manager, iv, result

    def test_log_stdout_no_file(self):
        pm, iv, _ = self.create_pm_with_function_and_run()
        assert len(self.mock_logs.messages['info']) == 2  # one log to run function, one log for result
        pyfileconf.options.set_option('log_stdout', True)
        pm.run(iv)
        assert len(self.mock_logs.messages['info']) == 5  # one log from function print in addition to two normal logs

    def test_log_file(self):
        logger.info('woo')
        assert not os.path.exists(self.logs_path)
        pyfileconf.options.set_option('log_folder', self.logs_folder)
        logger.info('woo2')
        pyfileconf.options.reset()
        logger.info('woo3')
        assert os.path.exists(self.logs_path)
        with open(self.logs_path, 'r') as f:
            contents = f.read()
            assert contents == '[pyfileconf INFO]: woo2\n'

    def test_log_stdout_file(self):
        pm, iv, _ = self.create_pm_with_function_and_run()
        assert len(self.mock_logs.messages['info']) == 2  # one log to run function, one log for result
        assert not os.path.exists(self.logs_path)
        pyfileconf.options.set_options([('log_stdout', True), ('log_folder', self.logs_folder)])
        pm.run(iv)
        assert len(self.mock_logs.messages['info']) == 5  # one log from function print in addition to two normal logs
        assert os.path.exists(self.logs_path)
        with open(self.logs_path, 'r') as f:
            contents = f.read()
            assert contents == '[pyfileconf INFO]: Running function stuff.a_function(\n\ta = None,\n\tb = None\n)\n[pyfileconf INFO]: print\n[pyfileconf INFO]: Result:\n(None, None)\n\n'
        pm.update(
            section_path_str=SectionPath('.'.join(iv.section_path_str.split('.')[1:])).path_str,
            b='raise_error'
        )
        pm.force_continue = True
        assert len(self.mock_logs.messages['error']) == 0
        pm.run(iv)
        assert len(self.mock_logs.messages['error']) == 2  # one for error at original time, one for error summary
        with open(self.logs_path, 'r') as f:
            contents = f.read()
            assert contents == '[pyfileconf INFO]: Running function stuff.a_function(\n\ta = None,\n\tb = None\n)\n[pyfileconf INFO]: print\n[pyfileconf INFO]: Result:\n(None, None)\n\n[pyfileconf INFO]: Running function stuff.a_function(\n\ta = None,\n\tb = r\'raise_error\'\n)\n[pyfileconf INFO]: print\n[pyfileconf ERROR]: Error while running stuff.a_function:\n\nTraceback (most recent call last):\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/main.py", line 646, in _try_except_run_func_except_user_interrupts\n    return try_func(**try_func_kwargs), True\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 112, in run\n    result = self._run(section_path_str_or_list)\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 146, in _run\n    return self._run_one_func(section_path_str)\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 191, in _run_one_func\n    result = func()\n  File "/home/nick/Dropbox/Python/py-file-conf/tests/input_files/amodule.py", line 25, in wrapper\n    return f(a, b)\n  File "/home/nick/Dropbox/Python/py-file-conf/tests/input_files/amodule.py", line 36, in a_function\n    raise ValueError(\'error was supposed to be raised\')\nValueError: error was supposed to be raised\n\n[pyfileconf ERROR]: Exception summary for running stuff.a_function (exceptions were also shown when raised):\nError while running stuff.a_function:\n\nTraceback (most recent call last):\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/main.py", line 646, in _try_except_run_func_except_user_interrupts\n    return try_func(**try_func_kwargs), True\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 112, in run\n    result = self._run(section_path_str_or_list)\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 146, in _run\n    return self._run_one_func(section_path_str)\n  File "/home/nick/Dropbox/Python/py-file-conf/pyfileconf/runner/models/runner.py", line 191, in _run_one_func\n    result = func()\n  File "/home/nick/Dropbox/Python/py-file-conf/tests/input_files/amodule.py", line 25, in wrapper\n    return f(a, b)\n  File "/home/nick/Dropbox/Python/py-file-conf/tests/input_files/amodule.py", line 36, in a_function\n    raise ValueError(\'error was supposed to be raised\')\nValueError: error was supposed to be raised\n\n'

