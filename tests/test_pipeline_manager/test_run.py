from copy import deepcopy

from pyfileconf import Selector, PipelineManager
from pyfileconf.iterate import IterativeRunner
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf import context
from tests.input_files.amodule import SecondExampleClass, a_function
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST, SAME_CLASS_CONFIG_DICT_LIST, \
    DIFFERENT_CLASS_CONFIG_DICT_LIST


class TestPipelineManagerRun(PipelineManagerTestBase):

    def test_run_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_run_function_multiple(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run([iv, iv])
        assert result == [(None, None), (None, None)]

    def test_run_function_multiple_pms(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Assert pipeline manager 1 run
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, None)

        # Assert pipeline manager 2 run
        iv = sel.test_pipeline_manager2.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_create_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

    def test_run_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        result = pipeline_manager.run(iv)
        assert result == 'woo'

    def test_create_class_multiple_pms(self):
        self.write_example_class_to_pipeline_dict_file()
        self.write_example_class_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Assert pipeline manager 1 create
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

        # Assert pipeline manager 2 create
        ec = sel.test_pipeline_manager2.stuff.ExampleClass()
        assert ec == ExampleClass(None)

    def test_create_from_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_run_from_specific_class_dict_original_execute_key(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        result = pipeline_manager.run(iv)
        assert result == 'woo'

    def test_run_from_specific_class_dict_custom_execute_key(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for config_dict in ccdl:
            config_dict['execute_attr'] = 'my_call'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        result = pipeline_manager.run(iv)
        assert result == 'woo2'

    def test_get_dependencies_while_running(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for config_dict in ccdl:
            config_dict['execute_attr'] = 'dependent_call'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.stuff.data2')
        pipeline_manager.create('example_class.stuff.data3')
        pipeline_manager.create('ec', ExampleClass)
        pipeline_manager.create('ec2', ExampleClass)
        pipeline_manager.create('ec3', ExampleClass)
        pipeline_manager.create('af', a_function)
        pipeline_manager.create('af2', a_function)
        pipeline_manager.create('af3', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        result = pipeline_manager.run(iv)
        assert context.config_dependencies == context.force_update_dependencies \
               == self.expect_pm_1_specific_class_depends_on_pm_1_specific_class_3_class_1_2_function_1_2

    def test_create_from_specific_class_dict_multiple_pms(self):
        self.write_example_class_dict_to_file()
        self.write_example_class_dict_to_file(pm_index=1)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Assert pipeline manager 1 create
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

        # Assert pipeline manager 2 create
        ec = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_create_from_multiple_specific_class_dicts_same_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(1)  # example_class2
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=SAME_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        ec2 = sel.test_pipeline_manager.example_class2.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == ec2.name == expect_ec.name
        assert ec.a == ec2.a == expect_ec.a

    def test_create_from_multiple_specific_class_dicts_different_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(2)  # second_example_class
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=DIFFERENT_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        sec = sel.test_pipeline_manager.second_example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        expect_sec = SecondExampleClass(name='data')
        assert ec.name == expect_sec.name == expect_ec.name
        assert ec.a == expect_ec.a
        assert sec.b == expect_sec.b


class TestPipelineManagerRunIter(PipelineManagerTestBase):

    def test_run_iter_function_single(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(
            section_path_str='stuff.a_function',
            b=10
        )
        config_dicts = [cd]
        result = pipeline_manager.run_iter(iv, config_dicts)
        assert result == [((cd,), (None, 10))]
        result = pipeline_manager.run_iter(iv, config_dicts, collect_results=False)
        assert result == []

    def test_run_iter_function_multiple(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        cd = dict(
            section_path_str='stuff.a_function',
            b=10,
            a=2
        )
        cd2 = dict(
            section_path_str='stuff.a_function',
            b=20
        )
        config_dicts = [cd, cd2]
        result = pipeline_manager.run_iter(iv, config_dicts)
        assert result == [((cd,), (2, 10)), ((cd2,), (None, 20))]
        result = pipeline_manager.run_iter(iv, config_dicts, collect_results=False)
        assert result == []

    def test_run_iter_function_multiple_pms(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        iv2 =sel.test_pipeline_manager2.stuff.a_function
        cd = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=10,
            a=2
        )
        cd2 = dict(
            section_path_str='test_pipeline_manager.stuff.a_function',
            b=20
        )
        cd3 = dict(
            section_path_str='test_pipeline_manager2.stuff.a_function',
            b=5,
            a=1
        )
        cd4 = dict(
            section_path_str='test_pipeline_manager2.stuff.a_function',
            b=7
        )
        config_dicts = [cd, cd2, cd3, cd4]
        runner = IterativeRunner([iv, iv2], config_dicts)
        result = runner.run()
        assert result == [((cd, cd3), [(2, 10), (1, 5)]), ((cd, cd4), [(2, 10), (None, 7)]),
                          ((cd2, cd3), [(None, 20), (1, 5)]), ((cd2, cd4), [(None, 20), (None, 7)])]
        result = runner.run(collect_results=False)
        assert result == []

    def test_run_iter_function_dependent_on_other_pm_class(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_example_class_dict_to_file(pm_index=1)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager2.load()
        self.append_to_a_function_config('a = s.test_pipeline_manager2.example_class.stuff.data')
        pipeline_manager.reload()
        sel = Selector()
        expected_a_result = ['a', 'b']
        iv = sel.test_pipeline_manager.stuff.a_function
        iv2 = sel.test_pipeline_manager2.example_class.stuff.data

        # Assert that update pipeline manager 2 affects pipeline manager 1
        cd = dict(
            a=expected_a_result,
            section_path_str=iv2.section_path_str
        )
        config_dicts = [cd]
        runner = IterativeRunner(iv, config_dicts)
        result = runner.run()
        assert result == [((cd,), (iv2, None))]
        assert iv2.a == expected_a_result
        assert context.config_dependencies == self.expect_pm_1_a_function_depends_on_pm_2_specific_class
