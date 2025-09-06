class MockLogResult:
    def __init__(self, data):
        self._filepath = "mocked_filepath"
        self._data = data

    def as_json(self):
        return self._data
