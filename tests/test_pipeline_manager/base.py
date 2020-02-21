import os
from typing import Optional
from unittest import TestCase

from pyfileconf import PipelineManager
from pyfileconf.main import create_project
from tests.input_files.amodule import SecondExampleClass, a_function
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.utils import delete_project, nested_pipeline_dict_str_with_obj, pipeline_dict_str_with_obj, \
    nested_class_dict_str, class_dict_str

BASE_GENERATED_DIR = os.path.join('tests', 'generated_files')
INPUT_FILES_DIR = os.path.join('tests', 'input_files')
EC_CLASS_DICT = {
    'class': ExampleClass,
    'name': 'example_class'
}
EC_CLASS_DICT2 = {
    'class': ExampleClass,
    'name': 'example_class2'
}
SEC_CLASS_DICT = {
    'class': SecondExampleClass,
    'name': 'second_example_class'
}
CLASS_CONFIG_DICT_LIST = [
    EC_CLASS_DICT
]
SAME_CLASS_CONFIG_DICT_LIST = [
    EC_CLASS_DICT,
    EC_CLASS_DICT2
]
DIFFERENT_CLASS_CONFIG_DICT_LIST = [
    EC_CLASS_DICT,
    SEC_CLASS_DICT
]
FULL_CLASS_DICT_LIST = [
    EC_CLASS_DICT,
    EC_CLASS_DICT2,
    SEC_CLASS_DICT
]


class PipelineManagerTestBase(TestCase):
    defaults_folder_name = 'custom_defaults'
    pm_folder = os.path.join(BASE_GENERATED_DIR, 'first')
    second_pm_folder = os.path.join(BASE_GENERATED_DIR, 'second')
    defaults_path = os.path.join(pm_folder, defaults_folder_name)
    second_defaults_path = os.path.join(pm_folder, defaults_folder_name)
    pipeline_dict_path = os.path.join(pm_folder, 'pipeline_dict.py')
    second_pipeline_dict_path = os.path.join(second_pm_folder, 'pipeline_dict.py')
    example_class_file_names = [
        'example_class_dict.py',
        'example_class2_dict.py',
        'second_example_class_dict.py',
    ]
    example_class_dict_paths = []
    for name in example_class_file_names:
        example_class_dict_paths.append(os.path.join(pm_folder, name))
    second_example_class_dict_paths = []
    for name in example_class_file_names:
        second_example_class_dict_paths.append(os.path.join(second_pm_folder, name))
    logs_path = os.path.join(pm_folder, 'MyLogs')
    all_paths = (
        defaults_path,
        pm_folder,
        *example_class_dict_paths,
        logs_path
    )
    test_name = 'test_pipeline_manager'
    second_test_name = 'test_pipeline_manager2'

    def setup_method(self, method):
        create_project(self.pm_folder, self.logs_path, FULL_CLASS_DICT_LIST)
        create_project(self.second_pm_folder, self.logs_path, FULL_CLASS_DICT_LIST)

    def teardown_method(self, method):
        delete_project(self.pm_folder, self.logs_path, FULL_CLASS_DICT_LIST)
        delete_project(self.second_pm_folder, self.logs_path, FULL_CLASS_DICT_LIST)

    def create_pm(self, **kwargs):
        all_kwargs = dict(
            folder=self.pm_folder,
            name=self.test_name,
            log_folder=self.logs_path,
            default_config_folder_name=self.defaults_folder_name,
        )
        all_kwargs.update(**kwargs)
        pipeline_manager = PipelineManager(**all_kwargs)
        return pipeline_manager

    def write_a_function_to_pipeline_dict_file(self, nest_section: bool = False, file_path: Optional[str] = None):
        if file_path is None:
            file_path = self.pipeline_dict_path

        if nest_section:
            write_str = nested_pipeline_dict_str_with_obj(
                a_function, 'my_section', 'stuff', 'tests.input_files.amodule'
            )
        else:
            write_str = pipeline_dict_str_with_obj(a_function, 'stuff', 'tests.input_files.amodule')
        with open(file_path, 'w') as f:
            f.write(write_str)

    def write_example_class_to_pipeline_dict_file(self, file_path: Optional[str] = None):
        if file_path is None:
            file_path = self.pipeline_dict_path
        with open(file_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(ExampleClass, 'stuff', 'tests.input_files.mypackage.cmodule'))

    def write_example_class_dict_to_file(self, idx: int = 0, nest_section: bool = False,
                                         pm_index: Optional[int] = 0):
        if pm_index == 0:
            ecdp = self.example_class_dict_paths
        elif pm_index == 1:
            ecdp = self.second_example_class_dict_paths
        else:
            raise ValueError(f'must pass 0 or 1 for pm_index, got {pm_index}')

        file_path = ecdp[idx]
        if nest_section:
            write_str = nested_class_dict_str('class_dict', 'my_section', 'stuff', 'data')
        else:
            write_str = class_dict_str('class_dict', 'stuff', 'data')
        with open(file_path, 'w') as f:
            f.write(write_str)