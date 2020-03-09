import os
from copy import deepcopy
from typing import Optional, Sequence

from pyfileconf import Selector
from pyfileconf.main import create_project
from tests.test_pipeline_manager.base import BASE_GENERATED_DIR, CLASS_CONFIG_DICT_LIST, PipelineManagerTestBase, \
    FULL_CLASS_DICT_LIST, SAME_CLASS_CONFIG_DICT_LIST, DIFFERENT_CLASS_CONFIG_DICT_LIST
from tests.utils import delete_project


def _assert_project_has_correct_files(folder: str):
    defaults_path = os.path.join(folder, 'defaults')
    pipeline_folder = folder
    pipeline_dict_path = os.path.join(pipeline_folder, 'pipeline_dict.py')
    example_class_dict_path = os.path.join(folder, 'example_class_dict.py')
    logs_path = os.path.join(folder, 'MyLogs')
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
    logs_path = os.path.join(BASE_GENERATED_DIR, 'MyLogs')
    delete_project(BASE_GENERATED_DIR, logs_path, CLASS_CONFIG_DICT_LIST)
    create_project(BASE_GENERATED_DIR, logs_path, CLASS_CONFIG_DICT_LIST)

    _assert_project_has_correct_files(BASE_GENERATED_DIR)

    delete_project(BASE_GENERATED_DIR, logs_path, CLASS_CONFIG_DICT_LIST)


class PipelineManagerLoadTestBase(PipelineManagerTestBase):

    def assert_default_imports_and_assigns_in_contents(self, contents: str):
        assert 'from pyfileconf import Selector' in contents
        assert 's = Selector()' in contents

    def assert_a_function_config_file_contents(self, contents: str):
        self.assert_default_imports_and_assigns_in_contents(contents)
        assert 'from typing import List' in contents
        assert 'from tests.input_files.mypackage.cmodule import ExampleClass' in contents
        assert 'a: ExampleClass = None' in contents
        assert 'b: List[str] = None' in contents

    def assert_example_class_config_file_contents(self, contents: str):
        self.assert_default_imports_and_assigns_in_contents(contents)
        assert 'import typing' in contents
        assert 'from typing import Optional' in contents
        assert 'a: typing.Tuple[int, int] = None' in contents
        assert 'name: Optional[str] = None' in contents

    def assert_example_class_dict_config_file_contents(self, contents: str, imports: Optional[Sequence[str]] = None,
                                                       assigns: Optional[Sequence[str]] = None,
                                                       a_value: str = 'a: typing.Tuple[int, int] = None',
                                                       name_value: str = "name: Optional[str] = 'data'"):
        if imports is None:
            imports = [
                'from pyfileconf import Selector',
            ]

        if assigns is None:
            assigns = [
                's = Selector()',
            ]

        # Always imports, from typing of arguments
        assert "from typing import Optional" in contents
        assert "import typing" in contents
        assert "import collections" in contents
        assert "from traceback import TracebackException" in contents

        # Always assigns, from arguments
        assert "c: Optional[collections.defaultdict] = None" in contents
        assert "d: Optional['TracebackException'] = None" in contents

        # TODO [#67]: format config output better, then update this test assertion
        #
        # For some reason, longer items when written to the config are line breaking at weird parts
        assert "f: typing.Sequence[typing.Union[collections.Counter, pathlib.Path]] " \
               "= (\n    collections.Counter(), collections.Counter(), pathlib.Path('.'))" in contents

        for item in imports + assigns + [a_value, name_value]:
            assert item in contents

    def assert_second_example_class_dict_config_file_contents(self, contents: str):
        assert "from typing import Optional" in contents
        assert "from tests.input_files.mypackage.cmodule import ExampleClass" in contents
        assert "s = Selector()" in contents
        assert "b: ExampleClass = None" in contents
        assert "name: Optional[str] = 'data'" in contents


class TestPipelineManagerLoad(PipelineManagerLoadTestBase):

    def test_create_empty_pm(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager

    def test_create_project_with_pm(self):
        delete_project(BASE_GENERATED_DIR, self.logs_path, FULL_CLASS_DICT_LIST)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=FULL_CLASS_DICT_LIST
        )
        pipeline_manager.load()
        _assert_project_has_correct_files(self.pm_folder)

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
            self.assert_a_function_config_file_contents(contents)

    def test_create_multiple_pms_with_function(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()

        # Assert pipeline manager 1 contents
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        module_folder = os.path.join(self.defaults_path, 'stuff')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)

        # Assert pipeline manager 2 contents
        sel = Selector()
        iv = sel.test_pipeline_manager2.stuff.a_function
        module_folder = os.path.join(self.second_defaults_path, 'stuff')
        function_path = os.path.join(module_folder, 'a_function.py')
        with open(function_path, 'r') as f:
            contents = f.read()
            self.assert_a_function_config_file_contents(contents)

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
            self.assert_example_class_config_file_contents(contents)

    def test_create_multiple_pms_with_class(self):
        self.write_example_class_to_pipeline_dict_file()
        self.write_example_class_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()

        # Assert pipeline manager 1 contents
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        module_folder = os.path.join(self.defaults_path, 'stuff')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)

        # Assert pipeline manager 2 contents
        sel = Selector()
        iv = sel.test_pipeline_manager2.stuff.ExampleClass
        module_folder = os.path.join(self.second_defaults_path, 'stuff')
        class_path = os.path.join(module_folder, 'ExampleClass.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_config_file_contents(contents)

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
            self.assert_example_class_dict_config_file_contents(contents)

    def test_create_multiple_pms_with_class_dict(self):
        self.write_example_class_dict_to_file()
        self.write_example_class_dict_to_file(pm_index=1)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Assert pipeline manager 1 contents
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)

        # Assert pipeline manager 2 contents
        iv = sel.test_pipeline_manager2.example_class.stuff.data
        class_folder = os.path.join(self.second_defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(contents)

    def test_create_pm_with_class_dict_and_custom_key_attr(self):
        self.write_example_class_dict_to_file()
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            key_attr='a'
        )
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=class_config_dict_list
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        class_folder = os.path.join(self.defaults_path, 'example_class')
        module_folder = os.path.join(class_folder, 'stuff')
        class_path = os.path.join(module_folder, 'data.py')
        with open(class_path, 'r') as f:
            contents = f.read()
            self.assert_example_class_dict_config_file_contents(
                contents,
                a_value="a: typing.Tuple[int, int] = 'data'",
                name_value="name: Optional[str] = None"
            )

    def test_create_pm_with_class_dict_and_imports(self):
        self.write_example_class_dict_to_file()
        always_imports = [
            'from copy import deepcopy',
            'from functools import partial'
        ]
        always_assigns = [

        ]
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_import_strs=always_imports,
            always_assign_strs=always_assigns,
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
            self.assert_example_class_dict_config_file_contents(
                contents,
                imports=always_imports,
                assigns=always_assigns
            )

    def test_create_pm_with_class_dict_and_assigns(self):
        self.write_example_class_dict_to_file()
        always_imports = [

        ]
        always_assigns = [
            'my_var = 6',
            'stuff = list((1,))'
        ]
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_import_strs=always_imports,
            always_assign_strs=always_assigns,
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
            self.assert_example_class_dict_config_file_contents(
                contents,
                imports=always_imports,
                assigns=always_assigns
            )

    def test_create_pm_with_class_dict_imports_and_assigns(self):
        self.write_example_class_dict_to_file()
        always_imports = [
            'from copy import deepcopy',
            'from functools import partial'
        ]
        always_assigns = [
            'my_var = 6',
            'stuff = list((1,))'
        ]
        class_config_dict_list = deepcopy(CLASS_CONFIG_DICT_LIST)
        class_config_dict_list[0].update(
            always_import_strs=always_imports,
            always_assign_strs=always_assigns,
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
            self.assert_example_class_dict_config_file_contents(
                contents,
                imports=always_imports,
                assigns=always_assigns
            )

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
                self.assert_example_class_dict_config_file_contents(contents)

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
            self.assert_example_class_dict_config_file_contents(contents)
        with open(class_paths[1], 'r') as f:
            contents = f.read()
            self.assert_second_example_class_dict_config_file_contents(contents)


class TestPipelineManagerInvalidLoad(PipelineManagerLoadTestBase):

    def test_create_pm_with_specific_class_name_matching_pipeline_name(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_example_class_dict_to_file()
        specific_class_config = deepcopy(CLASS_CONFIG_DICT_LIST)
        specific_class_config[0].update(name='stuff')  # make name match section in main dict
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=specific_class_config
        )
        with self.assertRaises(ValueError) as cm:
            pipeline_manager.load()
            exc = cm.exception
            assert 'cannot use a name for a specific class dict which is already specified ' \
                   'in top-level pipeline_dict' in str(exc)

    def test_create_pm_with_two_identical_specific_class_dicts(self):
        self.write_example_class_dict_to_file()  # example_class
        self.write_example_class_dict_to_file(1)  # example_class2
        specific_class_config = deepcopy(SAME_CLASS_CONFIG_DICT_LIST)
        # make name in second specific dict match that of first
        specific_class_config[1].update(name=specific_class_config[0]['name'])
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=specific_class_config,
        )
        with self.assertRaises(ValueError) as cm:
            pipeline_manager.load()
            exc = cm.exception
            assert 'cannot have multiple specific class dicts with the same name attribute. Got names' in str(exc)
