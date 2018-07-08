from typing import Tuple

from dero.manager.main import PipelineManager


def get_pipeline_dict_path_and_data_dict_path_from_manager(manager: PipelineManager) -> Tuple[str, str]:
    return manager.pipeline_dict_path, manager.data_dict_path