import unittest


class Pipe:
    def __init__(self, pipeline_input):
        self._pipeline_input = pipeline_input
        self._pipeline_output = None

    def output(self):
        return self._pipeline_input

    def step(self, step_name, step_function):
        self._pipeline_output = step_function(self._pipeline_input)
        return self


class PipeData:
    def __init__(self, filename):
        self._filename = filename


class MyTestCase(unittest.TestCase):
    def test_01(self):
        # Given
        filename = ""
        pipeline_input = [PipeData(filename)]

        # When
        pipe = Pipe(pipeline_input)

        # Then
        self.assertEqual(pipe.output(), pipeline_input)

    def test_02(self):
        # Given
        filename = ""
        pipeline_input = [PipeData(filename)]

        # When
        pipeline_output = PipeData(0)
        pipe = Pipe(pipeline_input).step("my_first_step", lambda algorithm: pipeline_output)

        # Then
        self.assertEqual(pipe.output(), pipeline_input)


if __name__ == '__main__':
    unittest.main()
