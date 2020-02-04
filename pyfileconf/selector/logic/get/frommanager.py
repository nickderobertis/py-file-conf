from typing import Tuple, Type, List, Dict, Union

from pyfileconf.main import PipelineManager


def get_pipeline_dict_path_and_specific_class_config_dicts_from_manager(manager: PipelineManager
                                                                        ) -> Tuple[
                                                                                str,
                                                                                List[Dict[str, Union[str, Type, List[str]]]]
                                                                        ]:
    return manager.pipeline_dict_path, manager.specific_class_config_dicts