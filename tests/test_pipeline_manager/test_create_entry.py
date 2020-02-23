import os

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
