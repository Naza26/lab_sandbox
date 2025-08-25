import os


def create_directory_from(path):
    os.makedirs(path, exist_ok=True)

def build_filesystem_path_from(directory, filename):
    return os.path.join(directory, filename)

def list_directory_contents(directory):
    return os.listdir(directory)

def last_part_of_path(path):
    return os.path.basename(path)