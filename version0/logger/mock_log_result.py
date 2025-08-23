class MockLogResult:
    def __init__(self, filepath):
        self._filepath = filepath

    def as_json(self):
        return {}
