from typing import Tuple, List, Union

ListOfStrs = List[str]
TwoNoneTuple = Tuple[None, None]
TwoStrTuple = Tuple[str, str]
TwoTupleNoneOrStr = Union[TwoStrTuple, TwoNoneTuple]

def _split_lines_into_import_and_assignment(lines: ListOfStrs, strip_lines=True) -> Tuple[ListOfStrs, ListOfStrs]:
    # TODO: deal with later imports
    # TODO: deal with use of import other than the word import
    import_section = []
    assignment_section = []
    # We can have three cases for the following two booleans:
    # The file starts in the import section (in_import_section=True, in_assignment_section=False).
    # Then, we enter the whitespace section between import and assignments.
    # This will be ignored (in_import_section=False, in_assignment_section=False)
    # Finally, once text is detected again after import section,
    # assignment section starts (in_import_section=False, in_assignment_section=True)
    in_import_section = True
    in_assignment_section = False
    for line in lines:

        if strip_lines:
            line = line.strip()

        # Handle import section
        if in_import_section:
            if 'import' in line:
                import_section.append(line)
            else:
                in_import_section = False  # no longer dealing with imports

        # Handle whitespace section in between import and assignment, and switching to assignment
        if not in_import_section and not in_assignment_section:
            if _is_whitespace_line(line):
                continue # skip whitespace inbetween import and assignment, but not between assignments or between imports
            else: # finished import section, found something other than whitespace. Must be in assignment section
                in_assignment_section = True

        # Assignment section, just output
        if in_assignment_section:
            assignment_section.append(line)

    return import_section, assignment_section

def _split_assignment_line_into_variable_name_and_assignment(line: str) -> TwoTupleNoneOrStr:

    # handle whitespace lines
    if '=' not in line:
        return None, None

    variable, value = tuple(item.strip() for item in line.split('='))
    return variable, value

def _is_whitespace_line(line: str) -> bool:
    return line.strip() == ''