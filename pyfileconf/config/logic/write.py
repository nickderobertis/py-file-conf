from pyfileconf.assignments.logic.write import _key_value_pair_to_assignment_str

def dict_as_function_kwarg_str(d: dict) -> str:
    lines = [_key_value_pair_to_assignment_str(key, value) for key, value in d.items()]

    return '\n\t' + ',\n\t'.join(lines) + '\n'




