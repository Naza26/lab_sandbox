from collections import deque

from logger.mock_log_result import MockLogResult


class MockFileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = f"{directory}/{filename}"
        return cls(path)

    def __init__(self, filepath):
        self._mocked_logs = deque()
        self._filepath = filepath

    def add_log(self, data):
        self._mocked_logs.extend([data])

    def is_empty(self):
        return len(self._mocked_logs) == 0

    def all_logs_as_json(self):
        log_data = self._mocked_logs.popleft()
        result = MockLogResult(log_data)
        return result.as_json()
