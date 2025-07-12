import unittest


class Pipe:
    def __init__(self, pipeline_input):
        self._pipeline_input = pipeline_input
        self._steps = []

    def output(self):
        return self.next_step_input()

    def step(self, step_name, step_function):
        self._steps.append(Step(step_name, self.next_step_input(), step_function))
        return self

    def next_step_input(self):
        if not self._steps:
            return self._pipeline_input
        return self._steps[-1].step_output()


class Step:
    def __init__(self, step_name, step_input, step_function):
        self._step_name = step_name
        self._step_function = step_function
        self._step_input = step_input
        self._step_output = PipeData(self._step_function(self._step_input.data()))

    def step_output(self):
        return self._step_output


class PipeData:
    def __init__(self, data):
        self._data = data

    def data(self):
        return self._data

    def __eq__(self, other):
        return self.data() == other.data()

    def __repr__(self):
        return str(self.data())


class PipeTestCase(unittest.TestCase):
    def test_01(self):
        # Given
        filename = ""
        pipeline_input = PipeData(filename)

        # When
        pipe = Pipe(pipeline_input)

        # Then
        self.assertEqual(pipe.output(), pipeline_input)

    def test_02(self):
        # Given
        pipeline_input = PipeData(0)

        # When
        pipeline_output = PipeData(1)
        pipe = Pipe(pipeline_input).step("my_first_step", lambda x: x + 1)

        # Then
        self.assertEqual(pipe.output(), pipeline_output)

    def test_03(self):
        # Given
        pipeline_input = PipeData(0)

        # When
        pipeline_output = PipeData(2)
        pipe = (Pipe(pipeline_input)
                .step("my_first_step", lambda x: x + 1)
                .step("my_second_step", lambda x: x + 1))

        # Then
        self.assertEqual(pipe.output(), pipeline_output)


if __name__ == '__main__':
    unittest.main()
