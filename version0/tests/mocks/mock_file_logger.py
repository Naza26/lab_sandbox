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

    def read_json_from_file(self):
        return self.all_logs()

    def write_json_to_file(self, data):
        pass

    def directory(self):
        return self._filepath.rsplit('/', 1)[0]

    def add_log(self, data):
        self._mocked_logs.extend([data])

    def is_empty(self):
        return len(self._mocked_logs) == 0

    def all_logs(self):
        if self.is_empty():
            return {}
        log_data = self._mocked_logs.popleft()
        result = MockLogResult(log_data)
        return result
