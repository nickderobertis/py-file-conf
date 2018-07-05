from typing import List


def combine_imports_lines_into_import_statements(multi_line_imports: List[str]) -> List[str]:
    import_statements_with_blanks = _combine_imports_lines_into_import_statements(multi_line_imports)
    return [import_str for import_str in import_statements_with_blanks if import_str.strip() != '']

def _combine_imports_lines_into_import_statements(multi_line_imports: List[str]) -> List[str]:

    parentheses = False
    continuing = False
    full_line = ''
    full_imports = []
    for line in multi_line_imports:
        if not continuing:
            full_line = ''
        if continuing and not parentheses:
            # backslash continues for one line. so now that we are on the next line, stop continuing
            continuing = False
        for word in line.split():
            if word.startswith('('):
                continuing = True
                parentheses = True
            elif word == '\\':
                continuing = True
                continue # don't add the backslash character itself, go to next word
            elif word.endswith(')'):
                parentheses = False
                continuing = False

            full_line += f'{word} '

        if not continuing:
            full_imports.append(full_line.strip())

    return full_imports