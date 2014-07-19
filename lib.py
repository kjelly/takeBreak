import os.path


def get_base_path():
    return os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
