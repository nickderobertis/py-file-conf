
class ImportException(Exception):
    pass


class NoImportStatementException(ImportException):
    pass


class CouldNotImportException(ImportException):
    pass


class NoImportMatchingNameException(ImportException):
    pass


class CouldNotExtractImportException(ImportException):
    pass


class CouldNotExtractModuleImportFromAstException(CouldNotExtractImportException):
    pass


class CouldNotExtractObjectImportFromAstException(CouldNotExtractImportException):
    pass


class CouldNotExtractRenameException(ImportException):
    pass


class CouldNotDetermineModuleForObjectException(ImportException):
    pass


class ExtractedIncorrectTypeOfImportException(ImportException):
    pass
