from copy import deepcopy

from pyfileconf import Selector, PipelineManager
from pyfileconf.iterate import IterativeRunner
from pyfileconf.sectionpath.sectionpath import SectionPath
from pyfileconf import context
from tests.input_files.amodule import SecondExampleClass, a_function
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST, SAME_CLASS_CONFIG_DICT_LIST, \
    DIFFERENT_CLASS_CONFIG_DICT_LIST


class TestUpdateContext(PipelineManagerTestBase):

    def test_update_currently_running_section_path_str_to_get_dependencies_while_running(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for config_dict in ccdl:
            config_dict['execute_attr'] = 'dependent_call_with_context_update'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        pipeline_manager.create('example_class.stuff.data2')
        pipeline_manager.create('example_class.stuff.data3')
        pipeline_manager.create('example_class.stuff.data4')
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
               == self.expect_pm_1_specific_class_4_depends_on_pm_1_specific_class_3_class_1_2_function_1_2
        assert context.currently_running_section_path_str is None


