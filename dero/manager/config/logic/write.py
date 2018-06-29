
def dict_as_local_definitions_str(d: dict):
    # TODO: add necessary import statements to output
    lines = [_key_value_pair_to_assignment_str(key, value) for key, value in d.items()]

    return '\n' + '\n'.join(lines) +'\n'


def _key_value_pair_to_assignment_str(key: str, value: any):
    value = _assignment_output_repr(value)
    return f'{key}={value}'


def _assignment_output_repr(value: any):
    # TODO: add special handling for other types here
    if callable(value):  # functions, classes, pull name
        return value.__name__
    if isinstance(value, str):
        return f"'{value}'"

    return value