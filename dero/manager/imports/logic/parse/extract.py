from typing import Tuple, List

from dero.manager.imports.logic.parse.patterns import re_patterns

def extract_line_without_comment_and_comment_from_line(line: str) -> Tuple[str, str]:
    # no comment
    if '#' not in line:
        return line, ''

    line = line.strip()
    # entire line is comment
    if line.startswith('#'):
        return '', line[1:]

    # comment is during line
    parts = line.split('#')
    return parts[0], '#'.join(parts[1:])