from typing import Tuple, List

ListOfStrs = List[str]


def _split_lines_into_import_and_assignment(lines: ListOfStrs, strip_lines=True) -> Tuple[ListOfStrs, ListOfStrs]:
    # TODO: deal with whitespace lines
    # TODO: deal with later imports
    # TODO: deal with use of import other than the word import
    import_section = []
    assignment_section = []
    in_import_section = True  # start the file in the import section, then after import statements, not in import section
    for line in lines:

        if strip_lines:
            line = line.strip()

        # Handle import section
        if in_import_section:
            if 'import' in line:
                import_section.append(line)
            else:
                in_import_section = False  # no longer dealing with imports

        # didn't use else, as in_import_section may change during that block
        if not in_import_section:
            assignment_section.append(line)

    return import_section, assignment_section