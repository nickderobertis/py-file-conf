import os

from pyfileconf import PipelineManager, create_project, Selector, DataSource
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.bmodule import ExampleClass
from tests.utils import delete_project, pipeline_dict_str_with_obj, class_dict_str
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


class PipelineManagerTestBase:
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

    def create_pm(self, **kwargs):
        all_kwargs = dict(
            pipeline_dict_path=self.pipeline_path,
            data_dict_path=self.data_dict_path,
            basepath=self.defaults_path,
            name=self.test_name,
            log_folder=self.logs_path,
        )
        all_kwargs.update(**kwargs)
        pipeline_manager = PipelineManager(**all_kwargs)
        return pipeline_manager

    def write_a_function_to_pipeline_dict_file(self):
        with open(self.pipeline_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(a_function, 'stuff', 'tests.input_files.amodule'))

    def write_example_class_to_pipeline_dict_file(self):
        with open(self.pipeline_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(ExampleClass, 'stuff', 'tests.input_files.bmodule'))

    def write_data_dict_to_file(self):
        with open(self.data_dict_path, 'w') as f:
            f.write(class_dict_str('data_dict', 'stuff', 'data'))

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
            assert 'a: Tuple[int, int] = None' in contents

    def test_create_pm_with_source(self):
        self.write_data_dict_to_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.sources.stuff.data
        sources_folder = os.path.join(self.defaults_path, 'sources')
        module_folder = os.path.join(sources_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            assert 'from pyfileconf import Selector' in contents
            assert 's = Selector()' in contents
            assert "name = 'data'" in contents
            assert "data_type = None" in contents
            assert "location = None" in contents
            assert "loader_func = None" in contents
            assert "pipeline = None" in contents
            assert "tags = None" in contents
            assert "loader_func_kwargs = dict()" in contents


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

    def test_create_data_source(self):
        self.write_data_dict_to_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        ds = sel.test_pipeline_manager.sources.stuff.data.item
        expect_ds = DataSource(name='data')
        assert ds.name == expect_ds.name
        assert ds.location == expect_ds.location



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

    # TODO [#33]: create update data source test should work after refactor for any arbitrary class as dict

    # def test_create_update_data_source(self):
    #     self.write_data_dict_to_file()
    #     pipeline_manager = self.create_pm()
    #     pipeline_manager.load()
    #     sel = Selector()
    #     iv = sel.test_pipeline_manager.sources.stuff.data
    #     expected_location_result = 'abc'
    #     section_path = SectionPath.from_section_str_list(SectionPath(iv.section_path_str)[1:])
    #     pipeline_manager.config.update(
    #         location=expected_location_result,
    #         section_path_str=section_path.path_str
    #     )
    #     ds = sel.test_pipeline_manager.sources.stuff.data.item
    #     expect_ds = DataSource(name='data', location=expected_location_result)
    #     assert ds.name == expect_ds.name
    #     assert ds.location == expect_ds.location


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

    def test_create_reload_class(self):
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
