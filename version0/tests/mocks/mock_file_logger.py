
from collections import deque

from tests.mocks.mock_log_result import MockLogResult


class MockFileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = f"{directory}/{filename}"
        return cls(path)

    def __init__(self, filepath):
        self._mocked_logs = deque()
        self._filepath = filepath
        self._current_trace_data = {}

    def read_json_from_file(self):
        return self._current_trace_data

    def write_json_to_file(self, data):
        self._current_trace_data = data
        self.add_log(data)

    def directory(self):
        return self._filepath.rsplit('/', 1)[0]

    def add_log(self, data):
        self._mocked_logs.append(data)

    def is_empty(self):
        return len(self._mocked_logs) == 0 and not self._current_trace_data

    def all_logs(self):
        if self._current_trace_data:
            return MockLogResult(self._current_trace_data)
        elif not self.is_empty():
            log_data = self._mocked_logs.popleft()
            return MockLogResult(log_data)
        else:
            return MockLogResult({})