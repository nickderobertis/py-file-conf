from copy import deepcopy
from typing import Sequence, Dict, Any, List, Tuple, Type, Optional, Iterable

from pyfileconf import (
    Selector,
    hookimpl,
    IterativeRunner,
    reset_plugins,
    remove_default_plugins,
    PipelineManager,
)
from pyfileconf.plugin import manager
from pyfileconf.runner.models.interfaces import RunnerArgs, ResultOrResults
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.amodule import a_function
from tests.test_pipeline_manager.base import (
    PipelineManagerTestBase,
    CLASS_CONFIG_DICT_LIST,
)

EXPECT_MODIFIED_CASES = [
    (
        dict(a=1, b=2, section_path_str="test_pipeline_manager.stuff.a_function"),
        dict(a=3, b=4, section_path_str="test_pipeline_manager.stuff.a_function"),
    )
]
EXTRA_CASE = (
    dict(a=5, b=6, section_path_str="test_pipeline_manager.stuff.a_function"),
)
EXTRA_RESULT = "abc"
OVERRIDDEN_B_RESULT = 10
PRE_RUN_COUNTER = 0
POST_RUN_COUNTER = 0
PRE_UPDATE_COUNTER = 0
POST_UPDATE_COUNTER = 0
ITER_UPDATE_COUNTER = 0
PRE_UPDATE_BATCH_COUNTER = 0
POST_UPDATE_BATCH_COUNTER = 0


class ExamplePlugin:
    @hookimpl
    def pyfileconf_iter_get_cases(
        self, config_updates: Sequence[Dict[str, Any]], runner: "IterativeRunner"
    ) -> List[Tuple[Dict[str, Any], ...]]:
        return EXPECT_MODIFIED_CASES

    @hookimpl
    def pyfileconf_iter_modify_cases(
        self, cases: List[Tuple[Dict[str, Any], ...]], runner: "IterativeRunner"
    ):
        cases.append(EXTRA_CASE)

    @hookimpl
    def pyfileconf_iter_update_for_case(
        case: Tuple[Dict[str, Any], ...], runner: "IterativeRunner"
    ):
        global ITER_UPDATE_COUNTER
        ITER_UPDATE_COUNTER += 1

    @hookimpl
    def pyfileconf_pre_run(
        self, section_path_str_or_list: RunnerArgs
    ) -> Optional[RunnerArgs]:
        global PRE_RUN_COUNTER
        PRE_RUN_COUNTER += 1
        return "stuff.a_function"

    @hookimpl
    def pyfileconf_post_run(
        self, results: ResultOrResults
    ) -> Optional[ResultOrResults]:
        global POST_RUN_COUNTER
        POST_RUN_COUNTER += 1
        return EXTRA_RESULT

    @hookimpl
    def pyfileconf_pre_update(
        self,
        pm: "PipelineManager",
        d: dict = None,
        section_path_str: str = None,
        kwargs: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        global PRE_UPDATE_COUNTER
        PRE_UPDATE_COUNTER += 1
        return dict(b=OVERRIDDEN_B_RESULT)

    @hookimpl
    def pyfileconf_post_update(
        self,
        pm: "PipelineManager",
        d: dict = None,
        section_path_str: str = None,
        kwargs: Dict[str, Any] = None,
    ):
        global POST_UPDATE_COUNTER
        POST_UPDATE_COUNTER += 1

    @hookimpl(trylast=True)
    def pyfileconf_pre_update_batch(
            pm: "PipelineManager",
            updates: Iterable[dict],
    ) -> Iterable[dict]:
        global PRE_UPDATE_BATCH_COUNTER
        PRE_UPDATE_BATCH_COUNTER += 1
        new_items = []
        for item in updates:
            new_update = {**item}
            new_update['b'] = OVERRIDDEN_B_RESULT
            new_items.append(new_update)
        return new_items

    @hookimpl
    def pyfileconf_post_update_batch(
        pm: "PipelineManager",
        updates: Iterable[dict],
    ):
        global POST_UPDATE_BATCH_COUNTER
        POST_UPDATE_BATCH_COUNTER += 1


class PluginsTest(PipelineManagerTestBase):
    def teardown_method(self, method):
        super().teardown_method(method)
        reset_plugins()
        self.reset_counters()

    def add_plugin(self, plugin_class: Type = ExamplePlugin):
        manager.plm.register(plugin_class())

    def replace_plugin(self, plugin_class: Type = ExamplePlugin):
        remove_default_plugins()
        self.add_plugin(plugin_class)

    def reset_counters(self):
        global PRE_RUN_COUNTER
        global POST_RUN_COUNTER
        global PRE_UPDATE_COUNTER
        global POST_UPDATE_COUNTER
        global ITER_UPDATE_COUNTER
        global PRE_UPDATE_BATCH_COUNTER
        global POST_UPDATE_BATCH_COUNTER
        PRE_RUN_COUNTER = 0
        POST_RUN_COUNTER = 0
        PRE_UPDATE_COUNTER = 0
        POST_UPDATE_COUNTER = 0
        ITER_UPDATE_COUNTER = 0
        PRE_UPDATE_BATCH_COUNTER = 0
        POST_UPDATE_BATCH_COUNTER = 0


class TestIterPlugins(PluginsTest):
    def test_iter_no_plugins(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=10, a=2)
        cd2 = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=20)
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [(cd,), (cd2,)]
        result = runner.run()
        assert result == [
            (
                (
                    {
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                        "b": 10,
                        "a": 2,
                    },
                ),
                (2, 10),
            ),
            (
                (
                    {
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                        "b": 20,
                    },
                ),
                (None, 20),
            ),
        ]

    def test_iter_add_plugin(self):
        self.add_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=10, a=2)
        cd2 = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=20)
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [*EXPECT_MODIFIED_CASES, (cd,), (cd2,), EXTRA_CASE]
        result = runner.run()
        assert result == [
            (
                (
                    {
                        "a": 1,
                        "b": 2,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                    {
                        "a": 3,
                        "b": 4,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                ),
                [(3, 10), (3, 10), "abc"],
            ),
            (
                (
                    {
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                        "b": 10,
                        "a": 2,
                    },
                ),
                [(2, 10), (2, 10), "abc"],
            ),
            (
                (
                    {
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                        "b": 20,
                    },
                ),
                [(None, 10), (None, 10), "abc"],
            ),
            (
                (
                    {
                        "a": 5,
                        "b": 6,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                ),
                [(5, 10), (5, 10), "abc"],
            ),
        ]

    def test_iter_replace_plugin(self):
        self.replace_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=10, a=2)
        cd2 = dict(section_path_str="test_pipeline_manager.stuff.a_function", b=20)
        config_dicts = [cd, cd2]
        runner = IterativeRunner(iv, config_dicts)
        assert runner.cases == [*EXPECT_MODIFIED_CASES, EXTRA_CASE]
        result = runner.run()
        assert ITER_UPDATE_COUNTER == 2
        assert result == [
            (
                (
                    {
                        "a": 1,
                        "b": 2,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                    {
                        "a": 3,
                        "b": 4,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                ),
                [(None, None), (None, None), "abc"],
            ),
            (
                (
                    {
                        "a": 5,
                        "b": 6,
                        "section_path_str": "test_pipeline_manager.stuff.a_function",
                    },
                ),
                [(None, None), (None, None), "abc"],
            ),
        ]


class TestRunPlugins(PluginsTest):
    def test_run_no_plugins(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, None)
        result = pipeline_manager.run([iv, iv])
        assert result == [(None, None), (None, None)]
        assert POST_RUN_COUNTER == 0
        assert PRE_RUN_COUNTER == 0

    def test_run_plugins(self):
        self.add_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == [(None, None), (None, None), EXTRA_RESULT]
        result = pipeline_manager.run([iv, iv])
        assert result == [(None, None), (None, None), (None, None), EXTRA_RESULT]
        assert POST_RUN_COUNTER == 2
        assert PRE_RUN_COUNTER == 2


class TestUpdatePlugins(PluginsTest):
    def test_update_no_plugins(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ["a", "b"]
        section_path = SectionPath.from_section_str_list(
            SectionPath(iv.section_path_str)[1:]
        )
        pipeline_manager.update(
            b=expected_b_result, section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)
        assert PRE_UPDATE_COUNTER == 0
        assert POST_UPDATE_COUNTER == 0

    def test_update_with_plugins(self):
        self.add_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ["a", "b"]
        section_path = SectionPath.from_section_str_list(
            SectionPath(iv.section_path_str)[1:]
        )
        pipeline_manager.update(
            b=expected_b_result, section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv)
        assert result == [
            (None, OVERRIDDEN_B_RESULT),
            (None, OVERRIDDEN_B_RESULT),
            "abc",
        ]
        assert PRE_UPDATE_COUNTER == 1
        assert POST_UPDATE_COUNTER == 1

    def test_update_batch_no_plugins(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('stuff2', a_function)
        sel = Selector()
        ivs = [
            sel.test_pipeline_manager.stuff.a_function,
            sel.test_pipeline_manager.stuff2.a_function,
        ]
        expected_b_result = ["a", "b"]
        updates = []
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(
                SectionPath(iv.section_path_str)[1:]
            )
            updates.append(dict(
                b=expected_b_result, section_path_str=section_path.path_str
            ))
        pipeline_manager.update_batch(updates)
        for iv in ivs:
            result = pipeline_manager.run(iv)
            assert result == (None, expected_b_result)
        assert PRE_UPDATE_BATCH_COUNTER == 0
        assert POST_UPDATE_BATCH_COUNTER == 0

    def test_update_batch_with_plugins(self):
        self.add_plugin()
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('stuff2', a_function)
        sel = Selector()
        ivs = [
            sel.test_pipeline_manager.stuff.a_function,
            sel.test_pipeline_manager.stuff2.a_function,
        ]
        expected_b_result = ["a", "b"]
        updates = []
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(
                SectionPath(iv.section_path_str)[1:]
            )
            updates.append(dict(
                b=expected_b_result, section_path_str=section_path.path_str
            ))
        pipeline_manager.update_batch(updates)
        for iv in ivs:
            result = pipeline_manager.run(iv)
            assert result == [
                (None, OVERRIDDEN_B_RESULT),
                (None, OVERRIDDEN_B_RESULT),
                "abc",
            ]
        assert PRE_UPDATE_BATCH_COUNTER == 1
        assert POST_UPDATE_BATCH_COUNTER == 1
