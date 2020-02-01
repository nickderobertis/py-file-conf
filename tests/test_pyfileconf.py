import os

from pyfileconf import PipelineManager

BASE_DIR = 'tests/input_files'

class TestPipelineManager:
    defaults_path = os.path.join(BASE_DIR, 'defaults')
    pipeline_path = os.path.join(BASE_DIR, 'pipeline_dict.py')
    data_dict_path = os.path.join(BASE_DIR, 'data_dict.py')
    logs_path = os.path.join(BASE_DIR, 'Logs')
    test_name = 'test_pipeline_manager'

    def test_create_empty_pm(self):
        pipeline_manager = PipelineManager(
            pipeline_dict_path=self.pipeline_path,
            data_dict_path=self.data_dict_path,
            basepath=self.defaults_path,
            name=self.test_name,
            log_folder=self.logs_path
        )
        pipeline_manager.load()