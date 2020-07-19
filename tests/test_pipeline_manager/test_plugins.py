from copy import deepcopy
from typing import Sequence, Dict, Any, List, Tuple, Type

from pyfileconf import Selector, hookimpl, IterativeRunner, reset_plugins, remove_default_plugins
from pyfileconf.plugin import manager
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST

EXPECT_MODIFIED_CASES = [(dict(a=1, b=2), dict(c=3, d=4))]
EXTRA_CASE = dict(e=5, f=6)


class ExamplePlugin:

    @hookimpl
    def pyfileconf_iter_get_cases(self, config_updates: Sequence[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], ...]]:
        return EXPECT_MODIFIED_CASES

    @hookimpl
    def pyfileconf_iter_modify_cases(self, cases: List[Tuple[Dict[str, Any], ...]]):
        cases.append(EXTRA_CASE)


class PluginsTest(PipelineManagerTestBase):

    def teardown_method(self, method):
        super().teardown_method(method)
        reset_plugins()

    def add_plugin(self, plugin_class: Type = ExamplePlugin):
        manager.plm.register(plugin_class())
        
    def replace_plugin(self, plugin_class: Type = ExamplePlugin):
        remove_default_plugins()
        self.add_plugin(plugin_class)


class TestIterPlugins(PluginsTest):

    def test_iter_no_plugins(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=10,
            a=2
        )
        cd2 = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=20
        )
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [(cd,), (cd2,)]

    def test_iter_add_plugin(self):
        self.add_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=10,
            a=2
        )
        cd2 = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=20
        )
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [*EXPECT_MODIFIED_CASES, (cd,), (cd2,), EXTRA_CASE]

    def test_iter_replace_plugin(self):
        self.replace_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=10,
            a=2
        )
        cd2 = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=20
        )
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [*EXPECT_MODIFIED_CASES, EXTRA_CASE]
