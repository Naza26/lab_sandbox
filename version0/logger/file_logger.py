import json


class FileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = cls.assert_file_can_be_created(filename, directory)
        return cls(path)

    @classmethod
    def assert_file_can_be_created(cls, filename, directory):
        import os
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Cannot create log file at {path}. Directory does not exist or is not writable.")
        return path

    def __init__(self, filepath):
        self._filepath = filepath
        self._create_log_directory_from_filepath()

    def is_empty(self):
        return self.all_logs_as_json() == {}

    def add_log(self):
        pass

    def all_logs_as_json(self):
        with open(self._filepath, "r") as file:
            return json.load(file)

    def _create_log_directory_from_filepath(self):
        with open(self._filepath, "w", encoding="utf-8") as file:
            file.write("{}")
