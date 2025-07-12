import unittest


class Pipe:
    def __init__(self, *inputs):
        self._pipeline_inputs = PipeData(list(inputs))
        self._steps = []

    def output(self):
        return self.next_step_input().data()

    def step(self, step_name, step_function):
        self._steps.append(Step(step_name, self.next_step_input(), step_function))
        return self

    def next_step_input(self):
        if not self._steps:
            return self._pipeline_inputs
        return self._steps[-1].step_output()


class Step:
    def __init__(self, step_name, step_input, step_function):
        self._step_name = step_name
        self._step_function = step_function
        self._step_input = step_input
        self._step_outputs = PipeData(self._step_function(step_input.data()))

    def step_output(self):
        return self._step_outputs


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
    def test_01_an_empty_pipeline_returns_input_as_output(self):
        # Given
        pipeline_input = 0

        # When
        pipe = Pipe(pipeline_input)

        # Then
        self.assertEqual(pipe.output(), [pipeline_input])

    def test_02_a_pipeline_can_execute_a_step_successfully(self):
        # Given
        pipeline_input = 0

        # When
        pipe = Pipe(pipeline_input).step("my_first_step", lambda x: [x[0] + 1])

        # Then
        self.assertEqual(pipe.output(), [1])

    def test_03_a_pipeline_can_execute_multiple_steps_successfully(self):
        # Given
        pipeline_input = 0

        # When
        pipe = (Pipe(pipeline_input)
                .step("my_first_step", lambda x: [x[0] + 1])
                .step("my_second_step", lambda x: [x[0] + 1]))

        # Then
        self.assertEqual(pipe.output(), [2])

    def test_04_a_pipeline_with_more_than_one_input_executes_successfully(self):
        # Given
        one_pipeline_input = 1
        another_pipeline_input = 1

        # When
        pipe = (Pipe(one_pipeline_input, another_pipeline_input)
                .step("my_first_step", lambda x: [x[0] + x[1]]))

        # Then
        self.assertEqual(pipe.output(), [2])


if __name__ == '__main__':
    unittest.main()
