import os

from pyfileconf import PipelineManager, create_project, Selector
from tests.utils import delete_project, pipeline_dict_str_with_func
from tests.input_files.amodule import a_function

BASE_GENERATED_DIR = os.path.join('tests', 'generated_files')
INPUT_FILES_DIR = os.path.join('tests', 'input_files')


def test_create_project():
    delete_project(BASE_GENERATED_DIR)
    create_project(BASE_GENERATED_DIR)

    defaults_path = os.path.join(BASE_GENERATED_DIR, 'defaults')
    pipeline_path = os.path.join(BASE_GENERATED_DIR, 'pipeline_dict.py')
    data_dict_path = os.path.join(BASE_GENERATED_DIR, 'data_dict.py')
    logs_path = os.path.join(BASE_GENERATED_DIR, 'Logs')
    all_paths = [
        defaults_path,
        pipeline_path,
        data_dict_path,
        logs_path
    ]
    for path in all_paths:
        assert os.path.exists(path)

    with open(pipeline_path, 'r') as f:
        contents = f.read()
        assert 'pipeline_dict = {}' in contents

    with open(data_dict_path, 'r') as f:
        contents = f.read()
        assert 'data_dict = {}' in contents

    delete_project(BASE_GENERATED_DIR)


class TestPipelineManagerLoad:
    defaults_path = os.path.join(BASE_GENERATED_DIR, 'defaults')
    pipeline_path = os.path.join(BASE_GENERATED_DIR, 'pipeline_dict.py')
    data_dict_path = os.path.join(BASE_GENERATED_DIR, 'data_dict.py')
    logs_path = os.path.join(BASE_GENERATED_DIR, 'Logs')
    all_paths = (
        defaults_path,
        pipeline_path,
        data_dict_path,
        logs_path
    )
    test_name = 'test_pipeline_manager'

    def setup_method(self, method):
        create_project(BASE_GENERATED_DIR)

    def teardown_method(self, method):
        delete_project(BASE_GENERATED_DIR)

    def test_create_empty_pm(self):
        pipeline_manager = PipelineManager(
            pipeline_dict_path=self.pipeline_path,
            data_dict_path=self.data_dict_path,
            basepath=self.defaults_path,
            name=self.test_name,
            log_folder=self.logs_path
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager

    def test_create_pm_with_function(self):
        with open(self.pipeline_path, 'w') as f:
            f.write(pipeline_dict_str_with_func(a_function, 'stuff', 'tests.input_files.amodule'))
        pipeline_manager = PipelineManager(
            pipeline_dict_path=self.pipeline_path,
            data_dict_path=self.data_dict_path,
            basepath=self.defaults_path,
            name=self.test_name,
            log_folder=self.logs_path
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        module_folder = os.path.join(self.defaults_path, 'stuff')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            assert 'a: str = None' in contents
            assert 'b: List[str] = None' in contents
            assert 'from typing import List' in contents
            assert 'from pyfileconf import Selector, MergeOptions' in contents
            assert 's = Selector()' in contents

