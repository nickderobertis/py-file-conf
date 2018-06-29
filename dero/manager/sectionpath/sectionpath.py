

class SectionPath:

    def __init__(self, section_path: str):
        self.path_str = section_path
        self.sections = _section_path_str_to_section_strs(section_path)

    def __iter__(self):
        for section in self.sections:
            yield section

    def __getitem__(self, item):
        return self.sections[item]


def _section_path_str_to_section_strs(section_path_str: str):
    return section_path_str.split('.')
