import json
import os

from utils import create_directory_from, build_filesystem_path_from


class FileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = cls.assert_file_can_be_created(filename, directory)
        return cls(path, directory)

    @classmethod
    def assert_file_can_be_created(cls, filename, directory):
        create_directory_from(directory)
        trace_path = build_filesystem_path_from(directory, filename)
        if not os.path.exists(trace_path):
            with open(trace_path, 'w') as f:
                f.write("{}")
        return trace_path

    def __init__(self, filepath, directory):
        self._filepath = filepath
        self._directory = directory

    def filepath(self):
        return self._filepath

    def directory(self):
        return self._directory

    def write_json_to_file(self, data):
        with open(self._filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def read_json_from_file(self):
        with open(self._filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    def is_empty(self):
        return self.all_logs_as_json() == {}

    def add_log(self):
        pass

    def all_logs_as_json(self):
        with open(self._filepath, "r") as file:
            return json.load(file)