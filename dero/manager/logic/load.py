from typing import Tuple
import os

from dero.manager.pipelines.logic.load import pipeline_dict_from_file
from dero.manager.data.logic.load import data_dict_from_file
from dero.manager.sectionpath.sectionpath import SectionPath

def get_pipeline_dict_and_data_dict_from_filepaths(pipeline_dict_path: str, data_dict_path: str) -> Tuple[dict, dict]:
    pipeline_section_path = SectionPath.from_filepath(os.getcwd(), pipeline_dict_path)
    pipeline_dict = pipeline_dict_from_file(pipeline_dict_path, module_name=pipeline_section_path.path_str)
    data_dict = data_dict_from_file(data_dict_path)

    return pipeline_dict, data_dict