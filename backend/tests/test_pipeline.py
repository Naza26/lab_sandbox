import unittest

from backend.business.pipeline import Pipeline


class PipelineTestCase(unittest.TestCase):
    def test_01_an_empty_pipeline_returns_input_as_output(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = Pipeline(pipeline_raw_input)

        # Then
        self.assertEqual(pipeline.output(), [pipeline_raw_input])

    def test_02_a_pipeline_can_execute_a_step_successfully(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = Pipeline(pipeline_raw_input).step("my_first_step", self._add_one)

        # Then
        expected_output = [1]
        self.assertEqual(pipeline.output(), expected_output)

    def test_03_a_pipeline_can_execute_multiple_steps_successfully(self):
        # Given
        pipeline_raw_input = 0

        # When
        pipeline = (Pipeline(pipeline_raw_input)
                    .step("my_first_step", self._add_one)
                    .step("my_second_step", self._add_one))

        # Then
        expected_output = [2]
        self.assertEqual(pipeline.output(), expected_output)

    def test_04_a_pipeline_with_more_than_one_input_executes_successfully(self):
        # Given
        one_raw_pipeline_input = 1
        another_raw_pipeline_input = 1

        # When
        pipeline = (Pipeline(one_raw_pipeline_input, another_raw_pipeline_input)
                    .step("my_first_step", self._sum_all))

        # Then
        expected_output = [2]
        self.assertEqual(pipeline.output(), expected_output)

    def _add_one(self, inputs):
        return [inputs[0] + 1]

    def _sum_all(self, inputs):
        return [sum(inputs)]


if __name__ == '__main__':
    unittest.main()
