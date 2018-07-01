from dero.manager.imports.logic.load.file import get_user_defined_dict_from_filepath
from dero.manager.pipelines.models.interfaces import PipelineDict

def pipeline_dict_from_file(filepath: str, module_name: str=None) -> PipelineDict:
    user_defined_dict = get_user_defined_dict_from_filepath(filepath, module_name=module_name)

    if 'pipeline_dict' not in user_defined_dict:
        raise ValueError(f'pipeline dict file {filepath} must contain variable pipeline_dict')

    return user_defined_dict['pipeline_dict']