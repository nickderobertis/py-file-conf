import os
from copy import deepcopy

from pyfileconf import Selector, PipelineManager, context
from pyfileconf.batch import BatchUpdater
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.amodule import SecondExampleClass, a_function
from tests.input_files.mypackage.cmodule import ExampleClass, ExampleClassWithCustomUpdate
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST, \
    SAME_CLASS_CONFIG_DICT_LIST, \
    DIFFERENT_CLASS_CONFIG_DICT_LIST, CUSTOM_UPDATE_CLASS_CONFIG_DICT_LIST


class TestPipelineManagerConfig(PipelineManagerTestBase):

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
        pipeline_manager.refresh(section_path.path_str)
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

    def test_config_update_function_multiple_dependent_pms(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        self.append_to_a_function_config('b = s.test_pipeline_manager2.stuff.a_function')
        pipeline_manager.reload()
        sel = Selector()
        expected_b_result = ['a', 'b']
        iv = sel.test_pipeline_manager.stuff.a_function
        iv2 = sel.test_pipeline_manager2.stuff.a_function

        # Assert original pipeline manager 1 has pipeline manager 2 a_function as b
        result = pipeline_manager.run(iv)
        assert result == (None, iv2)

        # Assert that update pipeline manager 2 affects pipeline manager 1
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv2)
        assert result == (None, iv2)
        assert result[1]() == (None, expected_b_result)
        assert context.config_dependencies == self.expect_pm_1_a_function_depends_on_pm_2_a_function

    def test_config_update_function_dependencies(self):
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
        pipeline_manager.update(
            section_path_str='stuff.a_function',
            b=sel.test_pipeline_manager2.stuff.a_function
        )
        assert context.config_dependencies == self.expect_pm_1_a_function_depends_on_pm_2_a_function

    def test_config_update_batch_functions(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('stuff2', a_function)
        sel = Selector()
        ivs = [
            sel.test_pipeline_manager.stuff.a_function,
            sel.test_pipeline_manager.stuff2.a_function,
        ]
        expected_b_result = ['a', 'b']
        updates = []
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
            updates.append(dict(
                b=expected_b_result,
                section_path_str=section_path.path_str
            ))
        pipeline_manager.update_batch(updates)
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
            result = pipeline_manager.run(iv)
            assert result == (None, expected_b_result)
            pipeline_manager.refresh(section_path.path_str)
            result = pipeline_manager.run(iv)
            assert result == (None, expected_b_result)

    def test_config_update_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        expected_f_value = 'woo'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        ec._f = expected_f_value
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)
        assert ec._f == expected_f_value
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)
        assert ec._f == expected_f_value

    def test_config_update_class_with_custom_update(self):
        self.write_example_class_with_custom_update_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClassWithCustomUpdate
        expected_a_result = (1, 2)
        expected_f_value = 'woo'
        assert iv._custom_update == 'a'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClassWithCustomUpdate()
        ec._f = expected_f_value
        ec = sel.test_pipeline_manager.stuff.ExampleClassWithCustomUpdate()
        assert ec == ExampleClassWithCustomUpdate(expected_a_result)
        assert ec._f == expected_f_value
        assert ec._custom_update == 'b'
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.stuff.ExampleClassWithCustomUpdate()
        assert ec == ExampleClassWithCustomUpdate(expected_a_result)
        assert ec._f == expected_f_value

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

    def test_create_update_class_multiple_dependent_pms(self):
        self.write_example_class_to_pipeline_dict_file()
        self.write_example_class_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        self.append_to_example_class_config('a = s.test_pipeline_manager2.stuff.ExampleClass')
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv2 = sel.test_pipeline_manager2.stuff.ExampleClass

        # Assert original pipeline manager 1 has pipeline manager 2 example class as a
        ec2 = sel.test_pipeline_manager2.stuff.ExampleClass
        expect_1 = ExampleClass(ec2)
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == expect_1
        assert ec.a().a is None

        # Assert that update pipeline manager 2 affects pipeline manager 1
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec2 = sel.test_pipeline_manager2.stuff.ExampleClass
        expect_1 = ExampleClass(ec2)
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == expect_1
        assert ec.a().a == ec._a().a == expected_a_result
        assert context.config_dependencies == self.expect_pm_1_class_depends_on_pm_2_class

    def test_config_update_class_dependencies(self):
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
        pipeline_manager.update(
            section_path_str='stuff.ExampleClass',
            a=sel.test_pipeline_manager2.stuff.ExampleClass
        )
        assert context.config_dependencies == self.expect_pm_1_class_depends_on_pm_2_class

    def test_config_update_batch_classes(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('stuff2', ExampleClass)
        sel = Selector()
        ivs = [
            sel.test_pipeline_manager.stuff.ExampleClass,
            sel.test_pipeline_manager.stuff2.ExampleClass,
        ]
        expected_a_result = (1, 2)
        expected_f_value = 'woo'
        updates = []
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
            updates.append(dict(
                a=expected_a_result,
                section_path_str=section_path.path_str
            ))
        pipeline_manager.update_batch(updates)
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
            ec = sel.test_pipeline_manager.stuff.ExampleClass()
            ec._f = expected_f_value
            ec = sel.test_pipeline_manager.stuff.ExampleClass()
            assert ec == ExampleClass(expected_a_result)
            assert ec._f == expected_f_value
            pipeline_manager.refresh(section_path.path_str)
            ec = sel.test_pipeline_manager.stuff.ExampleClass()
            assert ec == ExampleClass(expected_a_result)
            assert ec._f == expected_f_value

    def test_create_update_from_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        expected_f_result = 'woo'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.example_class.stuff.data
        # TODO [#108]: setting attribute on selector should set attribute on underlying object
        #
        # Modify the next line in this test to `ec._f = expected_f_result` and
        # it will show the need for this behavior
        ec.item._f = expected_f_result
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a
        assert ec._f == expected_f_result
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a
        assert ec._f == expected_f_result

    def test_create_update_from_specific_class_dict_with_custom_update(self):
        self.write_example_class_dict_to_file(3)  # index 3 is with custom update
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CUSTOM_UPDATE_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class_with_update.stuff.data
        expected_a_result = (1, 2)
        expected_f_result = 'woo'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.example_class_with_update.stuff.data
        ec.item._f = expected_f_result
        ec = sel.test_pipeline_manager.example_class_with_update.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a
        assert ec._f == expected_f_result
        assert ec._custom_update == 'b'
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.example_class_with_update.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a
        assert ec._f == expected_f_result
        assert ec._custom_update == 'b'

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
        assert ec.a == ec._a == expect_ec.a

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
        assert ec.a == ec._a == expect_ec.a

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
        assert ec.a == ec._a == expect_ec.a

    def test_create_update_from_specific_class_dict_multiple_dependent_pms(self):
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
        self.append_to_specific_class_config('a = s.test_pipeline_manager2.example_class.stuff.data')
        sel = Selector()
        iv2 = sel.test_pipeline_manager2.example_class.stuff.data

        # Assert original pipeline manager 1 has pipeline manager 2 example class as a
        ec2 = sel.test_pipeline_manager2.example_class.stuff.data
        expect_1 = ExampleClass(name='data', a=ec2)
        ec = sel.test_pipeline_manager.example_class.stuff.data.item
        assert ec == expect_1
        assert ec.a.a is None

        # Assert that update pipeline manager 2 affects pipeline manager 1
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv2.section_path_str)[1:])
        pipeline_manager2.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec2 = sel.test_pipeline_manager2.example_class.stuff.data
        expect_1 = ExampleClass(name='data', a=ec2)
        ec = sel.test_pipeline_manager.example_class.stuff.data.item
        assert ec == expect_1
        assert ec.a.a == ec._a.a == expected_a_result
        assert context.config_dependencies == self.expect_pm_1_specific_class_depends_on_pm_2_specific_class

    def test_create_update_specific_class_dependencies(self):
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
        pipeline_manager.update(
            section_path_str='example_class.stuff.data',
            a=sel.test_pipeline_manager2.example_class.stuff.data,
        )
        assert context.config_dependencies == self.expect_pm_1_specific_class_depends_on_pm_2_specific_class

    def test_create_update_from_specific_class_dict_multiple_dependent_attribute_pms(self):
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
        self.append_to_specific_class_config('a = s.test_pipeline_manager2.example_class.stuff.data.a')
        pipeline_manager.reload()
        sel = Selector()
        pipeline_manager.create('example_class.stuff.data2')
        self.append_to_specific_class_config('a = s.test_pipeline_manager.example_class.stuff.data2.a', pm_index=1)
        iv2 = sel.test_pipeline_manager2.example_class.stuff.data
        iv3 = sel.test_pipeline_manager.example_class.stuff.data2

        # Assert original pipeline manager 1 has pipeline manager 2 example class as a
        ec2 = sel.test_pipeline_manager2.example_class.stuff.data
        expect_1 = ExampleClass(name='data', a=ec2.a)
        ec = sel.test_pipeline_manager.example_class.stuff.data.item
        assert ec == expect_1
        assert ec.a is None

        # Assert original pipeline manager 2 has pipeline manager 1 example class 2 as a
        ec1_2 = sel.test_pipeline_manager.example_class.stuff.data2
        expect_2 = ExampleClass(name='data', a=ec1_2.a)
        ec = sel.test_pipeline_manager2.example_class.stuff.data.item
        assert ec == expect_2
        assert ec.a is None

        # Assert that update pipeline manager 1 ec 2 affects pipeline manager 2 ec which affects pipeline manager 1 ec 1
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv3.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        # Assert update affects pipeline manager 1 ec 1
        ec2 = sel.test_pipeline_manager2.example_class.stuff.data
        expect_1 = ExampleClass(name='data', a=ec2.a)
        ec = sel.test_pipeline_manager.example_class.stuff.data.item
        assert ec == expect_1
        assert ec.a == ec._a == expected_a_result
        # Assert update affects pipeline manager 2 ec 1
        ec2 = sel.test_pipeline_manager.example_class.stuff.data2
        expect_1 = ExampleClass(name='data', a=ec2.a)
        ec = sel.test_pipeline_manager2.example_class.stuff.data.item
        assert ec == expect_1
        assert ec.a == ec._a == expected_a_result
        assert context.config_dependencies == self.expect_pm_1_specific_class_depends_on_pm_2_specific_class_which_depends_on_pm_1_specific_class_2
        assert context.force_update_dependencies == self.expect_force_pm_1_specific_class_depends_on_pm_2_specific_class_which_depends_on_pm_1_specific_class_2

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
        assert ec.a == ec._a == ec2.a == ec2._a == expect_ec.a

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
        assert ec.a == ec._a == sec.b == expect_ec.a == expect_sec.b

    def test_create_update_batch_from_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.stuff.data2')
        sel = Selector()
        ivs = [
            sel.test_pipeline_manager.example_class.stuff.data,
            sel.test_pipeline_manager.example_class.stuff.data2,
        ]
        expected_a_result = (1, 2)
        expected_f_result = 'woo'
        updates = []
        for iv in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
            updates.append(dict(
                a=expected_a_result,
                section_path_str=section_path.path_str
            ))
        pipeline_manager.update_batch(updates)
        for ec in ivs:
            section_path = SectionPath.from_section_str_list(SectionPath(ec.section_path_str)[1:])
            ec = sel.test_pipeline_manager.example_class.stuff.data
            ec.item._f = expected_f_result
            ec = sel.test_pipeline_manager.example_class.stuff.data
            expect_ec = ExampleClass(name='data', a=expected_a_result)
            assert ec.name == expect_ec.name
            assert ec.a == ec._a == expect_ec.a
            assert ec._f == expected_f_result
            pipeline_manager.refresh(section_path.path_str)
            ec = sel.test_pipeline_manager.example_class.stuff.data
            expect_ec = ExampleClass(name='data', a=expected_a_result)
            assert ec.name == expect_ec.name
            assert ec.a == ec._a == expect_ec.a
            assert ec._f == expected_f_result

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

    def test_config_reset_function(self):
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
        pipeline_manager.reset(section_path.path_str)
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

    def test_config_reset_class(self):
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
        pipeline_manager.reset(section_path.path_str)
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
        assert ec.a == ec._a == expect_ec.a

    def test_config_reset_specific_class_dict(self):
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
        pipeline_manager.reset(section_path.path_str)
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a

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
        assert ec.a == ec._a == expect_ec.a

        # Assert that the reload of pipeline manager 1 did not affect pipeline manager 2
        ec = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a

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
        assert context.config_dependencies == self.expect_pm_1_a_function_depends_on_pm_1_specific_class

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
        assert ec.a == ec._a == expect_ec.a

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

    def test_invalid_config_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        self.write_error_to_a_function_file()

        # No error raised here thanks to lazy loading
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function

        # Config is only loaded once attribute of item view is accessed
        with self.assertRaises(ValueError):
            iv.item

    def test_invalid_config_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        self.write_error_to_example_class_file()

        # No error raised here thanks to lazy loading
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass

        # Config is only loaded once attribute of item view is accessed
        with self.assertRaises(ValueError):
            iv.item

    def test_invalid_specific_config_class(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        self.write_error_to_specific_example_class_file()

        # No error raised here thanks to lazy loading
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data

        # Config is only loaded once attribute of item view is accessed
        with self.assertRaises(ValueError):
            iv.item


class TestBatchUpdater(PipelineManagerTestBase):

    def test_config_batch_updater_function_multiple_pms(self):
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
        pms = [
            pipeline_manager,
            pipeline_manager2,
        ]
        ivs = [
            sel.test_pipeline_manager.stuff.a_function,
            sel.test_pipeline_manager2.stuff.a_function
        ]

        updates = []
        for iv in ivs:
            updates.append(dict(
                b=expected_b_result,
                section_path_str=iv.section_path_str
            ))

        bu = BatchUpdater()
        bu.update(updates)

        for pm, iv in zip(pms, ivs):
            result = pm.run(iv)
            assert result == (None, expected_b_result)

        sp_strs = [conf['section_path_str'] for conf in updates]
        bu.reset(sp_strs)

        for pm, iv in zip(pms, ivs):
            result = pm.run(iv)
            assert result == (None, None)

    def test_batch_updater_class_multiple_pms(self):
        self.write_example_class_to_pipeline_dict_file()
        self.write_example_class_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        pms = [
            pipeline_manager,
            pipeline_manager2,
        ]
        sel = Selector()
        expected_a_result = (1, 2)
        ivs = [
            sel.test_pipeline_manager.stuff.ExampleClass,
            sel.test_pipeline_manager2.stuff.ExampleClass,
        ]

        updates = []
        for iv in ivs:
            updates.append(dict(
                a=expected_a_result,
                section_path_str=iv.section_path_str
            ))

        bu = BatchUpdater()
        bu.update(updates)

        for iv in ivs:
            ec = iv()
            assert ec == ExampleClass(expected_a_result)

        sp_strs = [conf['section_path_str'] for conf in updates]
        bu.reset(sp_strs)

        for iv in ivs:
            ec = iv()
            assert ec == ExampleClass(None)

    def test_batch_updater_specific_class_dict_multiple_pms(self):
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
        pms = [
            pipeline_manager,
            pipeline_manager2,
        ]
        sel = Selector()
        expected_a_result = (1, 2)
        ivs = [
            sel.test_pipeline_manager.example_class.stuff.data,
            sel.test_pipeline_manager2.example_class.stuff.data,
        ]

        updates = []
        for iv in ivs:
            updates.append(dict(
                a=expected_a_result,
                section_path_str=iv.section_path_str
            ))

        bu = BatchUpdater()
        bu.update(updates)

        for ec in ivs:
            expect_ec = ExampleClass(name='data', a=expected_a_result)
            assert ec.name == expect_ec.name
            assert ec.a == ec._a == expect_ec.a

        sp_strs = [conf['section_path_str'] for conf in updates]
        bu.reset(sp_strs)

        for ec in ivs:
            expect_ec = ExampleClass(name='data', a=None)
            assert ec.name == expect_ec.name
            assert ec.a == ec._a == expect_ec.a


class TestConfigRefresh(PipelineManagerTestBase):
    # NOTE: refresh permanent tested in other tests in this file
    def test_refresh_transient_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str,
            pyfileconf_persist=False
        )
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)
        pipeline_manager.refresh(section_path.path_str)
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_refresh_transient_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        expected_f_value = 'woo'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str,
            pyfileconf_persist=False
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        ec._f = expected_f_value
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(expected_a_result)
        assert ec._f == expected_f_value
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)
        assert ec._f == expected_f_value

    def test_refresh_transient_specific_class(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        expected_f_result = 'woo'
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str,
            pyfileconf_persist=False
        )
        ec = sel.test_pipeline_manager.example_class.stuff.data
        ec.item._f = expected_f_result
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a
        assert ec._f == expected_f_result
        pipeline_manager.refresh(section_path.path_str)
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=None)
        assert ec.name == expect_ec.name
        assert ec.a == ec._a == expect_ec.a
        assert ec._f == expected_f_result
