from logger.mock_log_result import MockLogResult


class MockFileLogger:
    @classmethod
    def new_for(cls, filename, directory):
        path = f"{directory}/{filename}"
        return cls(path)

    def __init__(self, filepath):
        self._logs = {}
        self._filepath = filepath

    def is_empty(self):
        return self.all_logs_as_json() == {}

    def add_log(self, data):
        self._logs.update(data)

    def all_logs_as_json(self):
        result = MockLogResult(self._filepath) # FIXME: Replace with mock results
        return result.as_json()
