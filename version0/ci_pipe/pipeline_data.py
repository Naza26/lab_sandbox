class PipelineData:
    def __init__(self, *data):
        self._data = list(data)

    def data(self):
        return self._data

    def __eq__(self, other):
        return self.data() == other.data()

    def __repr__(self):
        return str(self.data())
