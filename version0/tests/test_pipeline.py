import unittest

from ci_pipe.pipeline import CIPipe
from ci_pipe.pipeline_data import PipelineData


class PipelineTestCase(unittest.TestCase):
    def test_01_an_empty_pipeline_returns_input_as_output(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = CIPipe(pipeline_raw_input)

        # Then
        self.assertEqual(pipeline.output(), [0])

    def test_02_a_pipeline_can_execute_a_step_successfully(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._add_one))

        # Then
        expected_output = {'result': 1}
        self.assertEqual(pipeline.output(), expected_output)

    def test_03_a_pipeline_can_execute_multiple_steps_successfully(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._add_one)
                    .step("my_second_step", self._add_another_one))

        # Then
        expected_output = {'result': 2}
        self.assertEqual(pipeline.output(), expected_output)

    def test_04_a_pipeline_with_more_than_one_input_executes_successfully(self):
        # Given
        one_raw_pipeline_input = 1
        another_raw_pipeline_input = 1

        # When
        pipeline = (CIPipe(one_raw_pipeline_input, another_raw_pipeline_input)
                    .step("my_first_step", self._sum_all))

        # Then
        expected_output = {'result': 2}
        self.assertEqual(pipeline.output(), expected_output)

    def test_05_can_get_pipeline_info(self):
        # Given
        one_raw_pipeline_input = 1
        another_raw_pipeline_input = 1

        # When
        pipeline = (CIPipe(one_raw_pipeline_input, another_raw_pipeline_input)
                    .step("my_first_step", self._sum_all))

        info = pipeline.info()

        expected_info = {
            'inputs': [1, 1],
            'output': {'result': 2},
            'steps': [
                {
                    'input': [1, 1],
                    'name': 'my_first_step',
                    'output': {'result': 2}
                }
            ]
        }

        # Then
        self.assertEqual(info, expected_info)

    def _add_one(self, inputs):
        return {'result': inputs[0] + 1}

    def _add_another_one(self, input):
        return {'result': input['result'] + 1}

    def _sum_all(self, inputs):
        return {'result': sum(inputs)}


if __name__ == '__main__':
    unittest.main()
