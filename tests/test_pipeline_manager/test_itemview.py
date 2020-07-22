import os
from copy import deepcopy

from pyfileconf import Selector, PipelineManager
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf.context import context
from pyfileconf.selector.models.itemview import ItemView
from tests.input_files.amodule import SecondExampleClass
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST, SAME_CLASS_CONFIG_DICT_LIST, \
    DIFFERENT_CLASS_CONFIG_DICT_LIST


class TestItemView(PipelineManagerTestBase):

    def assert_valid_function_iv(self, iv: ItemView, pipeline_manager: PipelineManager):
        assert isinstance(iv, ItemView)
        assert iv() == pipeline_manager.run(iv)
        assert iv.item() == pipeline_manager.get(iv)()

    def assert_valid_class_iv(self, iv: ItemView, pipeline_manager: PipelineManager):
        assert isinstance(iv, ItemView)
        assert iv() == pipeline_manager.get(iv)()
        assert iv()() == pipeline_manager.run(iv)
        assert iv.item() == pipeline_manager.get(iv)()

    def assert_valid_specific_class_iv(self, iv: ItemView, pipeline_manager: PipelineManager):
        assert isinstance(iv, ItemView)
        assert iv() == pipeline_manager.get(iv)()
        assert iv() == pipeline_manager.run(iv)
        assert iv.a == pipeline_manager.get(iv).a
        assert iv.item() == pipeline_manager.get(iv)()

    def test_function_iv_from_selector(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        self.assert_valid_function_iv(iv, pipeline_manager)

    def test_function_iv_from_str(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        iv = ItemView.from_section_path_str('test_pipeline_manager.stuff.a_function')
        self.assert_valid_function_iv(iv, pipeline_manager)

    def test_class_iv_from_selector(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        self.assert_valid_class_iv(iv, pipeline_manager)

    def test_class_iv_from_str(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        iv = ItemView.from_section_path_str('test_pipeline_manager.stuff.ExampleClass')
        self.assert_valid_class_iv(iv, pipeline_manager)

    def test_specific_class_iv_from_selector(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        self.assert_valid_specific_class_iv(iv, pipeline_manager)

    def test_specific_class_iv_from_str(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        iv = ItemView.from_section_path_str('test_pipeline_manager.example_class.stuff.data')
        self.assert_valid_specific_class_iv(iv, pipeline_manager)


