import os

from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.test_create import PipelineManagerLoadTestBase

from pyfileconf import Selector
from tests.input_files.amodule import a_function
from tests.test_pipeline_manager.base import PipelineManagerTestBase


class PipelineManagerCreateEntryTestBase(PipelineManagerLoadTestBase):
    pass


class TestPipelineManagerCreateEntry(PipelineManagerCreateEntryTestBase):

    def test_create_entry_for_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager.create(a_function, section_path_str='thing')
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
        pipeline_manager.create(ExampleClass, section_path_str='thing')
        sel = Selector()
        iv = sel.test_pipeline_manager.thing.ExampleClass
        module_folder = os.path.join(self.defaults_path, 'thing')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)