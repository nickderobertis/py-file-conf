import os

from pyfileconf import PipelineManager, create_project, Selector
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.bmodule import ExampleClass
from tests.utils import delete_project, pipeline_dict_str_with_obj, class_dict_str
from tests.input_files.amodule import a_function

BASE_GENERATED_DIR = os.path.join('tests', 'generated_files')
INPUT_FILES_DIR = os.path.join('tests', 'input_files')
CLASS_CONFIG_DICT_LIST = [
    {
        'class': ExampleClass,
        'name': 'example_class'
    }
]


def test_create_project():
    delete_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)
    create_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)

    defaults_path = os.path.join(BASE_GENERATED_DIR, 'defaults')
    pipeline_folder = BASE_GENERATED_DIR
    pipeline_dict_path = os.path.join(pipeline_folder, 'pipeline_dict.py')
    example_class_dict_path = os.path.join(BASE_GENERATED_DIR, 'example_class_dict.py')
    logs_path = os.path.join(BASE_GENERATED_DIR, 'Logs')
    all_paths = [
        defaults_path,
        pipeline_dict_path,
        example_class_dict_path,
        logs_path
    ]
    for path in all_paths:
        assert os.path.exists(path)

    with open(pipeline_dict_path, 'r') as f:
        contents = f.read()
        assert 'pipeline_dict = {}' in contents

    with open(example_class_dict_path, 'r') as f:
        contents = f.read()
        assert 'class_dict = {}' in contents

    delete_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)


class PipelineManagerTestBase:
    defaults_path = os.path.join(BASE_GENERATED_DIR, 'defaults')
    pipeline_folder = BASE_GENERATED_DIR
    pipeline_dict_path = os.path.join(pipeline_folder, 'pipeline_dict.py')
    example_class_dict_path = os.path.join(BASE_GENERATED_DIR, 'example_class_dict.py')
    logs_path = os.path.join(BASE_GENERATED_DIR, 'Logs')
    all_paths = (
        defaults_path,
        pipeline_folder,
        example_class_dict_path,
        logs_path
    )
    test_name = 'test_pipeline_manager'

    def setup_method(self, method):
        create_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)

    def teardown_method(self, method):
        delete_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)

    def create_pm(self, **kwargs):
        all_kwargs = dict(
            pipeline_dict_folder=self.pipeline_folder,
            basepath=self.defaults_path,
            name=self.test_name,
            log_folder=self.logs_path,
        )
        all_kwargs.update(**kwargs)
        pipeline_manager = PipelineManager(**all_kwargs)
        return pipeline_manager

    def write_a_function_to_pipeline_dict_file(self):
        with open(self.pipeline_dict_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(a_function, 'stuff', 'tests.input_files.amodule'))

    def write_example_class_to_pipeline_dict_file(self):
        with open(self.pipeline_dict_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(ExampleClass, 'stuff', 'tests.input_files.bmodule'))

    def write_example_class_dict_to_file(self):
        with open(self.example_class_dict_path, 'w') as f:
            f.write(class_dict_str('class_dict', 'stuff', 'data'))

class TestPipelineManagerLoad(PipelineManagerTestBase):

    def test_create_empty_pm(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager

    def test_create_pm_with_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        module_folder = os.path.join(self.defaults_path, 'stuff')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            assert 'from pyfileconf import Selector, MergeOptions' in contents
            assert 'from typing import List' in contents
            assert 'from tests.input_files.bmodule import ExampleClass' in contents
            assert 's = Selector()' in contents
            assert 'a: ExampleClass = None' in contents
            assert 'b: List[str] = None' in contents

    def test_create_pm_with_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        module_folder = os.path.join(self.defaults_path, 'stuff')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            assert 'from pyfileconf import Selector, MergeOptions' in contents
            assert 'from typing import Tuple' in contents
            assert 's = Selector()' in contents
            assert 'a: Optional[Tuple[int, int]] = None' in contents
            assert 'name: Optional[str] = None' in contents

    def test_create_pm_with_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            # TODO: once specific class file includes annotations, include them here
            assert "name = 'data'" in contents


def partialExampleClass(param):
    pass


class TestPipelineManagerRun(PipelineManagerTestBase):

    def test_run_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_create_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

    def test_create_from_specific_class_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a



class TestPipelineManagerConfig(PipelineManagerTestBase):

    def test_config_update_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.config.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        result = pipeline_manager.run(iv)
        assert result == (None, expected_b_result)

    def test_create_update_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
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
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a


    def test_config_reload_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        expected_b_result = ['a', 'b']
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.config.update(
            b=expected_b_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        result = pipeline_manager.run(iv)
        assert result == (None, None)

    def test_config_reload_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        expected_a_result = (1, 2)
        section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.stuff.ExampleClass()
        assert ec == ExampleClass(None)

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
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.reload()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(name='data')
        assert ec.name == expect_ec.name
        assert ec.a == expect_ec.a
