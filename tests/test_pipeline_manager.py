import os
from copy import deepcopy
from typing import Sequence, Type, Union, Dict, List

from pyfileconf import PipelineManager, Selector
from pyfileconf.main import create_project
from pyfileconf.sectionpath.sectionpath import SectionPath
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.utils import delete_project, pipeline_dict_str_with_obj, class_dict_str
from tests.input_files.amodule import a_function, SecondExampleClass

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

def _assert_project_has_correct_files(folder: str):
    defaults_path = os.path.join(folder, 'defaults')
    pipeline_folder = folder
    pipeline_dict_path = os.path.join(pipeline_folder, 'pipeline_dict.py')
    example_class_dict_path = os.path.join(folder, 'example_class_dict.py')
    logs_path = os.path.join(folder, 'Logs')
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


def test_create_project():
    delete_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)
    create_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)

    _assert_project_has_correct_files(BASE_GENERATED_DIR)

    delete_project(BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST)


class PipelineManagerTestBase:
    defaults_folder_name = 'custom_defaults'
    defaults_path = os.path.join(BASE_GENERATED_DIR, defaults_folder_name)
    pipeline_folder = BASE_GENERATED_DIR
    pipeline_dict_path = os.path.join(pipeline_folder, 'pipeline_dict.py')
    example_class_file_names = [
        'example_class_dict.py',
        'example_class2_dict.py',
        'second_example_class_dict.py',
    ]
    example_class_dict_paths = [os.path.join(BASE_GENERATED_DIR, name) for name in example_class_file_names]
    logs_path = os.path.join(BASE_GENERATED_DIR, 'Logs')
    all_paths = (
        defaults_path,
        pipeline_folder,
        *example_class_dict_paths,
        logs_path
    )
    test_name = 'test_pipeline_manager'

    def setup_method(self, method):
        create_project(BASE_GENERATED_DIR, FULL_CLASS_DICT_LIST)

    def teardown_method(self, method):
        delete_project(BASE_GENERATED_DIR, FULL_CLASS_DICT_LIST)

    def create_pm(self, **kwargs):
        all_kwargs = dict(
            folder=self.pipeline_folder,
            name=self.test_name,
            log_folder=self.logs_path,
            default_config_folder_name=self.defaults_folder_name,
        )
        all_kwargs.update(**kwargs)
        pipeline_manager = PipelineManager(**all_kwargs)
        return pipeline_manager

    def write_a_function_to_pipeline_dict_file(self):
        with open(self.pipeline_dict_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(a_function, 'stuff', 'tests.input_files.amodule'))

    def write_example_class_to_pipeline_dict_file(self):
        with open(self.pipeline_dict_path, 'w') as f:
            f.write(pipeline_dict_str_with_obj(ExampleClass, 'stuff', 'tests.input_files.mypackage.cmodule'))

    def write_example_class_dict_to_file(self, idx: int = 0):
        with open(self.example_class_dict_paths[idx], 'w') as f:
            f.write(class_dict_str('class_dict', 'stuff', 'data'))

class TestPipelineManagerLoad(PipelineManagerTestBase):

    def test_create_empty_pm(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager

    def test_create_project_with_pm(self):
        delete_project(BASE_GENERATED_DIR, FULL_CLASS_DICT_LIST)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=FULL_CLASS_DICT_LIST
        )
        pipeline_manager.load()
        _assert_project_has_correct_files(BASE_GENERATED_DIR)

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
            assert 'from pyfileconf import Selector' in contents
            assert 'from typing import List' in contents
            assert 'from tests.input_files.mypackage.cmodule import ExampleClass' in contents
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
            assert 'from pyfileconf import Selector' in contents
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
            assert "from typing import Optional" in contents
            assert "from typing import Tuple" in contents
            assert "from pyfileconf import Selector" in contents
            assert "s = Selector()" in contents
            assert "a: Optional[Tuple[int, int]] = None" in contents
            assert "name: Optional[str] = 'data'" in contents

    def test_create_pm_with_class_dict_and_imports(self):
        self.write_example_class_dict_to_file()
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_import_strs=[
                'from copy import deepcopy',
                'from functools import partial'
            ],
            always_assign_strs=[],
        )
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=class_config_dict_list,
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            assert "from typing import Optional" in contents
            assert "from typing import Tuple" in contents
            assert "from copy import deepcopy" in contents
            assert "from functools import partial" in contents
            assert "a: Optional[Tuple[int, int]] = None" in contents
            assert "name: Optional[str] = 'data'" in contents

    def test_create_pm_with_class_dict_and_assigns(self):
        self.write_example_class_dict_to_file()
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_assign_strs=[
                'my_var = 6',
                'stuff = list((1,))'
            ],
            always_import_strs=[],
        )
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=class_config_dict_list,
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            assert "from typing import Optional" in contents
            assert "from typing import Tuple" in contents
            assert "my_var = 6" in contents
            assert "stuff = list((1,))" in contents
            assert "a: Optional[Tuple[int, int]] = None" in contents
            assert "name: Optional[str] = 'data'" in contents

    def test_create_pm_with_class_dict_imports_and_assigns(self):
        self.write_example_class_dict_to_file()
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_import_strs=[
                'from copy import deepcopy',
                'from functools import partial'
            ],
            always_assign_strs=[
                'my_var = 6',
                'stuff = deepcopy(my_var)'
            ]
        )
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=class_config_dict_list,
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            assert "from typing import Optional" in contents
            assert "from typing import Tuple" in contents
            assert "from copy import deepcopy" in contents
            assert "from functools import partial" in contents
            assert "my_var = 6" in contents
            assert "stuff = deepcopy(my_var)" in contents
            assert "a: Optional[Tuple[int, int]] = None" in contents
            assert "name: Optional[str] = 'data'" in contents

    def test_create_pm_with_multiple_class_dicts_same_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(1)  # example_class2
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=SAME_CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folders = [
            os.path.join(self.defaults_path, 'example_class'),
            os.path.join(self.defaults_path, 'example_class2'),
        ]
        module_folders = [os.path.join(class_folder, 'stuff') for class_folder in class_folders]
        class_paths = [os.path.join(module_folder, 'data.py') for module_folder in module_folders]
        for class_path in class_paths:
            with open(class_path, 'r') as f:
                contents = f.read()
                assert "from typing import Optional" in contents
                assert "from typing import Tuple" in contents
                assert "s = Selector()" in contents
                assert "a: Optional[Tuple[int, int]] = None" in contents
                assert "name: Optional[str] = 'data'" in contents

    def test_create_pm_with_multiple_class_dicts_different_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(2)  # second_example_class
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=DIFFERENT_CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folders = [
            os.path.join(self.defaults_path, 'example_class'),
            os.path.join(self.defaults_path, 'second_example_class'),
        ]
        module_folders = [os.path.join(class_folder, 'stuff') for class_folder in class_folders]
        class_paths = [os.path.join(module_folder, 'data.py') for module_folder in module_folders]
        with open(class_paths[0], 'r') as f:
            contents = f.read()
            assert "from typing import Optional" in contents
            assert "from typing import Tuple" in contents
            assert "s = Selector()" in contents
            assert "a: Optional[Tuple[int, int]] = None" in contents
            assert "name: Optional[str] = 'data'" in contents
        with open(class_paths[1], 'r') as f:
            contents = f.read()
            assert "from typing import Optional" in contents
            assert "from tests.input_files.mypackage.cmodule import ExampleClass" in contents
            assert "s = Selector()" in contents
            assert "b: ExampleClass = None" in contents
            assert "name: Optional[str] = 'data'" in contents

    # TODO [#37]: test invalid inputs
    #
    # such as specific class name matching pipeline name, passing two of the same names for classes, etc.

    # TODO [#41]: test multiple simultaneous pipeline managers
    #
    # need create, get, run tests

    # TODO [#42]: test referencing object in a function config through selector and updating that object
    #
    # Should see that updating the object with `config.update` will cause the function pointing to
    # the selector for that object to use the updated object.


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

    def test_create_from_multiple_specific_class_dicts_same_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(1)  # example_class2
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=SAME_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        ec2 = sel.test_pipeline_manager.example_class2.stuff.data
        expect_ec = ExampleClass(name='data')
        assert ec.name == ec2.name == expect_ec.name
        assert ec.a == ec2.a == expect_ec.a

    def test_create_from_multiple_specific_class_dicts_different_class(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(2)  # second_example_class
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=DIFFERENT_CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        ec = sel.test_pipeline_manager.example_class.stuff.data
        sec = sel.test_pipeline_manager.second_example_class.stuff.data
        expect_ec = ExampleClass(name='data')
        expect_sec = SecondExampleClass(name='data')
        assert ec.name == expect_sec.name == expect_ec.name
        assert ec.a == expect_ec.a
        assert sec.b == expect_sec.b


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
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.config.update(
            a=expected_a_result,
            section_path_str=section_path2.path_str
        )
        expect_ec = ExampleClass(name='data', a=expected_a_result)
        assert ec.name == ec2.name == expect_ec.name
        assert ec.a == ec2.a == expect_ec.a

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
        pipeline_manager.config.update(
            a=expected_result,
            section_path_str=section_path.path_str
        )
        pipeline_manager.config.update(
            b=expected_result,
            section_path_str=section_path_s.path_str
        )
        expect_ec = ExampleClass(name='data', a=expected_result)
        expect_sec = SecondExampleClass(name='data', b=expected_result)
        assert ec.name == sec.name == expect_ec.name
        assert ec.a == sec.b == expect_ec.a == expect_sec.b

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
