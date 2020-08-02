import pyfileconf
from pyfileconf.opts import options

from tests.test_pipeline_manager.base import PipelineManagerTestBase


class OptionsTest(PipelineManagerTestBase):

    def teardown_method(self, method):
        super().teardown_method(method)
        pyfileconf.options.reset()


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
