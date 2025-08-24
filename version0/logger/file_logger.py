import json
import os


class FileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = cls.assert_file_can_be_created(filename, directory)
        return cls(path)

    @classmethod
    def assert_file_can_be_created(cls, filename, directory):
        path = os.path.join(directory, filename)
        dirpath = os.path.dirname(path) or "."
        os.makedirs(dirpath, exist_ok=True)  # create logs/ if missing

        # Probe writability by opening the file for append (creates if absent)
        try:
            with open(path, "a", encoding="utf-8"):
                pass
        except OSError as e:
            raise FileNotFoundError(
                f"Cannot create log file at {path}. Directory does not exist or is not writable."
            ) from e
        return path

    def __init__(self, filepath):
        self._filepath = filepath
        self._create_log_directory_from_filepath()

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

    def _create_log_directory_from_filepath(self):
        with open(self._filepath, "w", encoding="utf-8") as file:
            file.write("{}")
