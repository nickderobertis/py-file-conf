from copy import deepcopy

from pyfileconf import Selector
from tests.input_files.mypackage.cmodule import ExampleClass
from tests.test_pipeline_manager.base import PipelineManagerTestBase, CLASS_CONFIG_DICT_LIST


class TestPipelineManagerGetOne(PipelineManagerTestBase):

    def test_get_function(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        iv_func = pipeline_manager.get(iv)
        iv_result = iv_func()
        str_func = pipeline_manager.get('stuff.a_function')
        str_result = str_func()
        assert iv_func is str_func is iv.item
        assert iv_result == str_result == (None, None)

    def test_get_function_multiple_pms(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Get from pipeline manager 1
        iv = sel.test_pipeline_manager.stuff.a_function
        iv_func = pipeline_manager.get(iv)
        iv_result = iv_func()
        str_func = pipeline_manager.get('stuff.a_function')
        str_result = str_func()
        assert iv_result == str_result == (None, None)

        # Get from pipeline manager 2
        iv = sel.test_pipeline_manager2.stuff.a_function
        iv_func = pipeline_manager2.get(iv)
        iv_result = iv_func()
        str_func = pipeline_manager2.get('stuff.a_function')
        str_result = str_func()
        assert iv_result == str_result == (None, None)

    def test_get_class(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('stuff.ExampleClass')
        assert iv_obj is str_obj is iv()
        assert iv_obj == ExampleClass(None)

    def test_get_class_multiple_pms(self):
        self.write_example_class_to_pipeline_dict_file()
        self.write_example_class_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Get from pipeline manager 1
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('stuff.ExampleClass')
        assert iv_obj is str_obj is iv()
        assert iv_obj == ExampleClass(None)

        # Get from pipeline manager 2
        iv = sel.test_pipeline_manager2.stuff.ExampleClass
        iv_obj = pipeline_manager2.get(iv)
        str_obj = pipeline_manager2.get('stuff.ExampleClass')
        assert iv_obj is str_obj is iv()
        assert iv_obj == ExampleClass(None)

    def test_get_class_from_specific_config_dict(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv_obj is str_obj is iv.item
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_class_from_specific_config_dict_custom_name(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        self.append_to_specific_class_config('name: str = "My Name"')
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='My Name')
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv_obj is str_obj is iv.item
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_class_from_specific_config_dict_custom_key_attr_and_key(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for cd in ccdl:
            cd['key_attr'] = 'c'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        self.append_to_specific_class_config('c: str = "My Name"')
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, c='My Name', name=None)
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv_obj is str_obj is iv.item
        assert iv_obj.c == str_obj.c == expect_ec.c
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_class_from_specific_config_dict_multiple_pms(self):
        self.write_example_class_dict_to_file()
        self.write_example_class_dict_to_file(pm_index=1)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Get from pipeline manager 1
        iv = sel.test_pipeline_manager.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

        # Get from pipeline manager 2
        iv = sel.test_pipeline_manager2.example_class.stuff.data
        expect_ec = ExampleClass(None, name='data')
        iv_obj = pipeline_manager2.get(iv)
        str_obj = pipeline_manager2.get('example_class.stuff.data')
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_consistent_specific_config_obj(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv.item is iv_obj is str_obj

    def test_get_class_from_specific_config_dict_access_property_that_needs_obj_loaded(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff.data
        pipeline_manager.update(
            a=(1, 2),
            section_path_str='example_class.stuff.data'
        )
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv.e == iv_obj.e == str_obj.e == 10


class TestPipelineManagerGetSection(PipelineManagerTestBase):

    def test_get_main_dict_section(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff
        iv_section = pipeline_manager.get(iv)
        iv_func = iv_section[0]
        iv_result = iv_func()
        str_section = pipeline_manager.get('stuff')
        str_func = str_section[0]
        str_result = str_func()
        direct_iv_func = iv.a_function.item
        direct_str_func = pipeline_manager.get('stuff.a_function')
        assert iv_func is str_func is direct_iv_func is direct_str_func
        assert iv_result == str_result == (None, None)

    def test_get_main_dict_section_multiple_pms(self):
        self.write_a_function_to_pipeline_dict_file()
        self.write_a_function_to_pipeline_dict_file(file_path=self.second_pipeline_dict_path)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Get pipeline manager 1 section
        iv = sel.test_pipeline_manager.stuff
        iv_section = pipeline_manager.get(iv)
        iv_func = iv_section[0]
        iv_result = iv_func()
        str_section = pipeline_manager.get('stuff')
        str_func = str_section[0]
        str_result = str_func()
        assert iv_result == str_result == (None, None)

        # Get pipeline manager 2 section
        iv = sel.test_pipeline_manager2.stuff
        iv_section = pipeline_manager2.get(iv)
        iv_func = iv_section[0]
        iv_result = iv_func()
        str_section = pipeline_manager2.get('stuff')
        str_func = str_section[0]
        str_result = str_func()
        assert iv_result == str_result == (None, None)

    def test_get_main_dict_nested_section(self):
        self.write_a_function_to_pipeline_dict_file(nest_section=True)
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.my_section
        iv_section = pipeline_manager.get(iv)
        iv_func = iv_section['stuff'][0]
        iv_result = iv_func()
        str_section = pipeline_manager.get('my_section')
        str_func = str_section['stuff'][0]
        str_result = str_func()
        assert iv_result == str_result == (None, None)

    def test_get_specific_class_dict_section(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff
        expect_ec = ExampleClass(None, name='data')
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager.get('example_class.stuff')
        str_obj = str_section[0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_specific_class_dict_section_custom_name(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        self.append_to_specific_class_config('name: str = "My Name"')
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff
        expect_ec = ExampleClass(None, name='My Name')
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager.get('example_class.stuff')
        str_obj = str_section[0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_specific_class_dict_section_custom_key_attr_and_key(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for cd in ccdl:
            cd['key_attr'] = 'c'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        self.append_to_specific_class_config('c: str = "My Name"')
        pipeline_manager.reload()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff
        expect_ec = ExampleClass(None, c='My Name', name=None)
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager.get('example_class.stuff')
        str_obj = str_section[0]
        direct_iv_obj = pipeline_manager.get(iv.data)
        direct_str_obj = pipeline_manager.get('example_class.stuff.data')
        assert iv_obj is str_obj is direct_iv_obj is direct_str_obj
        assert iv_obj.c == str_obj.c == expect_ec.c
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_specific_class_dict_section_multiple_pms(self):
        self.write_example_class_dict_to_file()
        self.write_example_class_dict_to_file(pm_index=1)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        pipeline_manager2 = self.create_pm(
            folder=self.second_pm_folder,
            name=self.second_test_name,
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST,
        )
        pipeline_manager2.load()
        sel = Selector()

        # Get pipeline manager 1 section
        iv = sel.test_pipeline_manager.example_class.stuff
        expect_ec = ExampleClass(None, name='data')
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager.get('example_class.stuff')
        str_obj = str_section[0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

        # Get pipeline manager 2 section
        iv = sel.test_pipeline_manager2.example_class.stuff
        expect_ec = ExampleClass(None, name='data')
        iv_section = pipeline_manager2.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager2.get('example_class.stuff')
        str_obj = str_section[0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_specific_class_dict_nested_section(self):
        self.write_example_class_dict_to_file(nest_section=True)
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class
        expect_ec = ExampleClass(None, name='data')
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section['my_section']['stuff'][0]
        str_section = pipeline_manager.get('example_class')
        str_obj = str_section['my_section']['stuff'][0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a

    def test_get_specific_class_dict_custom_key_attr_section(self):
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
        iv = sel.test_pipeline_manager.example_class.stuff
        expect_ec = ExampleClass(a='data')
        iv_section = pipeline_manager.get(iv)
        iv_obj = iv_section[0]
        str_section = pipeline_manager.get('example_class.stuff')
        str_obj = str_section[0]
        assert iv_obj.name == str_obj.name == expect_ec.name
        assert iv_obj.a == str_obj.a == expect_ec.a


class TestGetSectionPathFromItem(PipelineManagerTestBase):

    def test_get_function_section_path(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.a_function
        iv_run = iv()  # result of a_function(), should not have _section_path_str
        assert not hasattr(iv_run, '_section_path_str')
        iv_func = pipeline_manager.get(iv)
        str_func = pipeline_manager.get('stuff.a_function')
        for obj in [iv, iv_func, str_func]:
            sp = obj._section_path_str
            assert sp == 'test_pipeline_manager.stuff.a_function'

    def test_get_function_section_path_by_section(self):
        self.write_a_function_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff
        iv_func = pipeline_manager.get(iv)
        str_func = pipeline_manager.get('stuff')
        assert iv._section_path_str == 'test_pipeline_manager.stuff'
        for obj_list in [iv_func, str_func]:
            for obj in obj_list:
                sp = obj._section_path_str
                assert sp == 'test_pipeline_manager.stuff.a_function'

    def test_get_class_section_path(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff.ExampleClass
        iv_run = iv()  # running general class gets instance of class, so should have _section_path_str
        iv_class = pipeline_manager.get(iv)
        str_class = pipeline_manager.get('stuff.ExampleClass')
        for obj in [iv, iv_run, iv_class, str_class]:
            sp = obj._section_path_str
            assert sp == 'test_pipeline_manager.stuff.ExampleClass'

    def test_get_class_section_path_by_section(self):
        self.write_example_class_to_pipeline_dict_file()
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.stuff
        iv_class = pipeline_manager.get(iv)
        str_class = pipeline_manager.get('stuff')
        assert iv._section_path_str == 'test_pipeline_manager.stuff'
        for obj_list in [iv_class, str_class]:
            for obj in obj_list:
                sp = obj._section_path_str
                assert sp == 'test_pipeline_manager.stuff.ExampleClass'

    def test_get_specific_class_section_path(self):
        self.write_example_class_dict_to_file()
        ccdl = deepcopy(CLASS_CONFIG_DICT_LIST)
        for config_dict in ccdl:
            config_dict['execute_attr'] = 'return_section_path_str'
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=ccdl
        )
        pipeline_manager.load()
        sel = Selector()
        assert sel.test_pipeline_manager.example_class.stuff.data.return_section_path_str() == \
               'test_pipeline_manager.example_class.stuff.data'
        iv = sel.test_pipeline_manager.example_class.stuff.data
        # result of __call__ on ExampleClass, should not have _section_path_str on result, but should have in object
        iv_run = iv()
        pm_run = pipeline_manager.run(iv)
        assert not hasattr(iv_run, '_section_path_str')
        assert iv_run == pm_run == 'test_pipeline_manager.example_class.stuff.data'
        # attribute access should be normal, not have _section_path_str
        iv_attr = iv.a
        assert not hasattr(iv_attr, '_section_path_str')
        assert iv_attr is None
        # property access should be normal, not have _section_path_str
        iv_property = iv.my_property
        assert not hasattr(iv_property, '_section_path_str')
        assert iv_property == 100
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff.data')
        for obj in [iv, iv_obj, str_obj]:
            sp = obj._section_path_str
            assert sp == 'test_pipeline_manager.example_class.stuff.data'

    def test_get_specific_class_section_path_by_section(self):
        self.write_example_class_dict_to_file()
        pipeline_manager = self.create_pm(
            specific_class_config_dicts=CLASS_CONFIG_DICT_LIST
        )
        pipeline_manager.load()
        sel = Selector()
        iv = sel.test_pipeline_manager.example_class.stuff
        iv_obj = pipeline_manager.get(iv)
        str_obj = pipeline_manager.get('example_class.stuff')
        assert iv._section_path_str == 'test_pipeline_manager.example_class.stuff'
        for obj_list in [iv_obj, str_obj]:
            for obj in obj_list:
                sp = obj._section_path_str
                assert sp == 'test_pipeline_manager.example_class.stuff.data'