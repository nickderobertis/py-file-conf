import os

from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.test_create import PipelineManagerLoadTestBase

from pyfileconf import Selector
from tests.input_files.amodule import a_function
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST


class PipelineManagerCreateEntryTestBase(PipelineManagerLoadTestBase):
    pass


class TestPipelineManagerCreateEntry(PipelineManagerCreateEntryTestBase):

    def test_create_entry_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.a_function
        module_folder = os.path.join(self.defaults_path, 'thing')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)

    def test_create_entry_for_previously_unimported_function(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.a_function
        module_folder = os.path.join(self.defaults_path, 'thing')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)
        module_folder = os.path.join(self.defaults_path, 'stuff')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)

    def test_update_then_create_entry_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        orig_iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(orig_iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.create('thing', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.a_function
        module_folder = os.path.join(self.defaults_path, 'thing')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)
        result = pipeline_manager.run(orig_iv)
        assert result == (None, expected_b_result)

    def test_create_then_update_entry_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        module_folder = os.path.join(self.defaults_path, 'thing')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

    def test_create_entry_for_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing', ExampleClass)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.ExampleClass
        module_folder = os.path.join(self.defaults_path, 'thing')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)

    def test_create_entry_for_previously_unimported_class(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing', ExampleClass)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.ExampleClass
        module_folder = os.path.join(self.defaults_path, 'stuff')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)
        module_folder = os.path.join(self.defaults_path, 'thing')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)

    def test_create_entry_for_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.thing.data')
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.thing.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'thing')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)

    def test_update_then_create_entry_for_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        orig_iv = sel.test_pipeline_manager.example_class.stuff.data
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(orig_iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.create('example_class.thing.data')
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.thing.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'thing')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_create_then_update_entry_for_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.thing.data')
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.thing.data
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'thing')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)
        ec = sel.test_pipeline_manager.example_class.thing.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a

    def test_create_deeply_nested_entry_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create('thing.stuff.whoa', a_function)
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.stuff.whoa.a_function
        module_folder = os.path.join(self.defaults_path, 'thing')
        module_folder = os.path.join(module_folder, 'stuff')
        module_folder = os.path.join(module_folder, 'whoa')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)

    def test_create_deeply_nested_entry_for_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.thing.stuff.whoa.data')
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.thing.stuff.whoa.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'thing')
        module_folder = os.path.join(module_folder, 'stuff')
        module_folder = os.path.join(module_folder, 'whoa')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)

    def test_create_entry_for_specific_class_dict_in_same_section_as_existing_entry(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.stuff.data2')
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data2
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data2.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(
                contents,
                name_value="name: Optional[str] = 'data2'"
            )
