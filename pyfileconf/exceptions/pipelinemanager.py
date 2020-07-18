from pyfileconf.exceptions.base import ManagerException


class PipelineManagerNotLoadedException(ManagerException):
    pass


class NoPipelineManagerForFilepathException(ManagerException):
    pass


class NoPipelineManagerForSectionPathException(ManagerException):
    pass