from enum import Enum


class PyfileconfActions(Enum):
    RUN = 'run'
    LOAD_FILE_EXECUTE = 'load_file_execute'
    LOAD_FILE_AST = 'load_file_ast'
    LOAD_PIPELINE_FILE_AST = 'load_pipeline_file_ast'
