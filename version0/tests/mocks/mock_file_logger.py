from tests.mocks.mock_log_result import MockLogResult

class MockFileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = f"{directory}/{filename}"
        return cls(path)

    def __init__(self, filepath):
        self._filepath = filepath
        self._current_trace = {}

    def read_json_from_file(self):
        return self._current_trace

    def write_json_to_file(self, data):
        self._current_trace = data

    def all_logs(self):
        return MockLogResult(self._current_trace)

    def directory(self):
        return self._filepath.rsplit('/', 1)[0]

    def add_log(self, data):
        pass

    def is_empty(self):
        return len(self._current_trace) == 0