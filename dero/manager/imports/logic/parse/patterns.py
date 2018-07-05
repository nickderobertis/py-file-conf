import re

patterns = {
    'obj import': r'from\s+([\w\.]+)\s+import((\s+\w+,?)+\s*)',
    'module import': 'import((\s+[\w\.]+,?)+)\s*',
    'rename': '\w+\s+as\s+\w+',
    'rename parts': '(\w+)\s+as\s+(\w+)',
}
re_patterns = {name: re.compile(pattern) for name, pattern in patterns.items()}