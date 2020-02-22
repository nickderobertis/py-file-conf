import os
from copy import deepcopy

from pyfileconf import Selector
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.amodule import SecondExampleClass
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST, SAME_CLASS_CONFIG_DICT_LIST, \
    DIFFERENT_CLASS_CONFIG_DICT_LIST


class TestPipelineManagerConfig(PipelineManagerTestBase):

    def append_to_a_function_config(self, to_add: str):
        section_folder = os.path.join(self.defaults_path, 'stuff')
        config_path = os.path.join(section_folder, 'a_function.py')
        with open(config_path, 'a') as f:
            f.write(to_add)

    def append_to_example_class_config(self, to_add: str):
        section_folder = os.path.join(self.defaults_path, 'stuff')
        config_path = os.path.join(section_folder, 'ExampleClass.py')
        with open(config_path, 'a') as f:
            f.write(to_add)

    def append_to_specific_class_config(self, to_add: str):
        class_folder = os.path.join(self.defaults_path, 'example_class')
        section_folder = os.path.join(class_folder, 'stuff')
        config_path = os.path.join(section_folder, 'data.py')
        with open(config_path, 'a') as f:
            f.write(to_add)

    def test_config_update_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

    def test_config_update_by_file_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        expected_b_result = ['a', 'b']
        b_str = f'b = {expected_b_result}'
        self.append_to_a_function_config(b_str)
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

    def test_config_update_function_multiple_pms(self):
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
        expected_b_result = ['a', 'b']
        iv = sel.test_pipeline_manager.stuff.a_function
        iv2 = sel.test_pipeline_manager2.stuff.a_function

        # Assert update pipeline manager 1
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

        # Assert that pipeline manager 2 is not updated yet
        result2 = pipeline_manager2.run(iv2)
        assert result2 == (None, None)

        # Assert update pipeline manager 2
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager2.run(iv2)
        assert result == (None, expected_b_result)

    def test_config_update_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

    def test_config_update_by_file_for_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        expected_a_result = (1, 2)
        a_str = f'a = {expected_a_result}'
        self.append_to_example_class_config(a_str)
        pipeline_manager.reload()
        sel = Selector()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

    def test_create_update_class_multiple_pms(self):
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
        expected_a_result = (1, 2)
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv2 = sel.test_pipeline_manager2.stuff.ExampleClass

        # Assert update pipeline manager 1
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

        # Assert that pipeline manager 2 is not updated yet
        ec = sel.test_pipeline_manager2.stuff.ExampleClass()
        assert ec == ExampleClass(None)

        # Assert update pipeline manager 2
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager2.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

    def test_create_update_from_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_config_update_by_file_for_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        expected_a_result = (1, 2)
        a_str = f'a = {expected_a_result}'
        self.append_to_specific_class_config(a_str)
        pipeline_manager.reload()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_create_update_from_specific_class_dict_multiple_pms(self):
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
        expected_a_result = (1, 2)
        iv = sel.test_pipeline_manager.example_class.stuff.data
        iv2 = sel.test_pipeline_manager2.example_class.stuff.data

        # Assert update pipeline manager 1
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

        # Assert that pipeline manager 2 is not updated yet
        ec = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

        # Assert update pipeline manager 2
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_create_update_from_multiple_specific_class_dicts_same(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(1)  # example_class2
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=SAME_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        ec2 = sel.test_pipeline_manager.example_class2.stuff.data
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(ec.section_path_str)[1:])
        section_path2 = SectionPath.from_section_str_list(SectionPath(ec2.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path2.path_str
        )
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == ec2.name == expect_ec.name
        assert ec.a == ec2.a == expect_ec.a

    def test_create_update_from_multiple_specific_class_dicts_different(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(2)  # second_example_class
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=DIFFERENT_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        sec = sel.test_pipeline_manager.second_example_class.stuff.data
        expected_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(ec.section_path_str)[1:])
        section_path_s = SectionPath.from_section_str_list(SectionPath(sec.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.update(
            b=expected_result,
            section_path_str=section_path_s.path_str
        )
        expect_ec = ExampleClass(name='data', a=expected_result)
        expect_sec = SecondExampleClass(name='data', b=expected_result)
        assert ec.name == sec.name == expect_ec.name
        assert ec.a == sec.b == expect_ec.a == expect_sec.b

    def test_config_reload_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_config_reload_function_multiple_pms(self):
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
        iv2 = sel.test_pipeline_manager2.stuff.a_function
        expected_b_result = ['a', 'b']

        # Update both pipeline manager configs
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )

        # Assert that reloading pipeline manager 1 resets its config
        pipeline_manager.reload()
        result = pipeline_manager.run(iv)
        assert result == (None, None)

        # Assert that the reload of pipeline manager 1 did not affect pipeline manager 2
        result = pipeline_manager2.run(iv2)
        assert result == (None, expected_b_result)

    def test_config_reload_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

    def test_config_reload_class_multiple_pms(self):
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
        expected_a_result = (1, 2)
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv2 = sel.test_pipeline_manager2.stuff.ExampleClass

        # Update both pipeline manager configs
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )

        # Assert that reloading pipeline manager 1 resets its config
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

        # Assert that the reload of pipeline manager 1 did not affect pipeline manager 2
        ec = sel.test_pipeline_manager2.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

    def test_config_reload_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_config_reload_specific_class_dict_multiple_pms(self):
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
        expected_a_result = (1, 2)
        iv = sel.test_pipeline_manager.example_class.stuff.data
        iv2 = sel.test_pipeline_manager2.example_class.stuff.data

        # Update both pipeline manager configs
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )

        # Assert that reloading pipeline manager 1 resets its config
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

        # Assert that the reload of pipeline manager 1 did not affect pipeline manager 2
        ec = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_config_update_class_used_by_function_through_selector(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager.load()

        # Link function to specific class object
        b_str = 'b = s.test_pipeline_manager.example_class.stuff.data'
        self.append_to_a_function_config(b_str)

        # Update specific class object config file to ensure we are getting the correct one later
        expected_a_result = (1, 2)
        a_str = f'a = {expected_a_result}'
        self.append_to_specific_class_config(a_str)

        pipeline_manager.reload()
        sel = Selector()

        # Assert that we can already get the specific class object returned before updating config
        f_iv = sel.test_pipeline_manager.stuff.a_function
        sc_iv = sel.test_pipeline_manager.example_class.stuff.data
        result = pipeline_manager.run(f_iv)
        sc = pipeline_manager.get(sc_iv)
        expect_sc = ExampleClass(a=expected_a_result, name='data')
        result_none, result_sc = result
        assert result_none is None
        assert result_sc.name == sc.name == expect_sc.name
        assert result_sc.a == sc.a == expect_sc.a

        # Assert that updating the specific class object updates the result from the function
        second_expected_a_result = (3, 4)
        section_path = SectionPath.from_section_str_list(SectionPath(sc_iv.section_path_str)[1:])
        pipeline_manager.update(
            a=second_expected_a_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(f_iv)
        sc = pipeline_manager.get(sc_iv)
        expect_sc = ExampleClass(a=second_expected_a_result, name='data')
        result_none, result_sc = result
        assert result_none is None
        assert result_sc.name == sc.name == expect_sc.name
        assert result_sc.a == sc.a == expect_sc.a

    def test_config_update_function_by_item_view(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        iv.b = expected_b_result
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

    def test_config_update_class_by_item_view(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        iv.a = expected_a_result
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)

    def test_update_specific_class_config_attr_by_item_view(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        iv.a = expected_a_result
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_deep_copy_specific_class_dict_item_view(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        new_item = deepcopy(iv)
        assert isinstance(new_item, ExampleClass)
        assert iv.item is not new_item
