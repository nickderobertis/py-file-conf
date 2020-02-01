import os
import shutil


def delete_project(path: str):
    all_paths = [
        os.path.join(path, 'defaults'),
        os.path.join(path, 'pipeline_dict.py'),
        os.path.join(path, 'data_dict.py'),
        os.path.join(path, 'Logs'),
    ]
    for path in all_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            # Must not exist, maybe add handling for this later
            pass
