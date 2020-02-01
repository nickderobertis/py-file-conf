from typing import Tuple, List, Union, Sequence
from copy import deepcopy

ListOfStrs = List[str]
TwoNoneTuple = Tuple[None, None]
TwoStrTuple = Tuple[str, str]
TwoTupleNoneOrStr = Union[TwoStrTuple, TwoNoneTuple]

def _split_lines_into_import_and_assignment(lines: ListOfStrs, strip_lines=True) -> Tuple[ListOfStrs, ListOfStrs]:
    # TODO [#2]: deal with later imports
    #
    # Imports can currently only be read from the top of the file

    # TODO [#3]: deal with use of import other than the word import

    import_section = []
    assignment_section = []
    # We can have three cases for the following two booleans:
    # The file starts in the import section
    # Then, we enter the whitespace section between import and assignments. Still consider this the import section.
    # Finally, once text is detected again after import section,
    # assignment section starts (in_import_section=False)
    in_import_section = True
    for i, line in enumerate(lines):

        if strip_lines:
            line = line.strip('\n')

        # Handle import section and add whitespace below import section
        if in_import_section:
            if 'import' in line or _is_whitespace_line(line):
                import_section.append(line)
            else:
                in_import_section = False  # no longer dealing with imports, must have assignment line

        # Assignment section, just output
        if not in_import_section:
            assignment_section.append(line)

    # Import section was handled as both import section and following whitespace. Strip following whitespace.
    import_section = _strip_whitespace_lines_from_end_of_lines(import_section)

    return import_section, assignment_section

def _split_assignment_line_into_variable_name_and_assignment(line: str) -> TwoTupleNoneOrStr:

    # handle whitespace lines
    if '=' not in line:
        return None, None

    # Split into two parts by the first equals (handle multiple equals). Treating further equals as string
    # TODO [#4]: handle multiple assignments such as this = that = 5
    split_line = line.split('=')
    parts: Sequence[str]
    if len(split_line) > 2:
        parts = split_line[0], '='.join(split_line[1:])
    else:
        parts = split_line

    variable, value = tuple(item.strip() for item in parts)
    return variable, value

def _is_whitespace_line(line: str) -> bool:
    return line.strip() == ''

def _strip_whitespace_lines_from_end_of_lines(lines: List[str]) -> List[str]:

    # Handle empty list
    if lines == []:
        return []

    reversed_lines = deepcopy(lines)
    reversed_lines.reverse()

    # starting from end first. Discard all lines until non-whitespace is found
    for line_index, line in enumerate(reversed_lines):
        if not _is_whitespace_line(line):
            break

    output_lines = reversed_lines[line_index:]
    output_lines.reverse() # back to first first

    return output_lines

