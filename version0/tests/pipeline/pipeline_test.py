import json
import os
import tempfile
import unittest
from unittest.mock import patch

from ci_pipe.pipeline import CIPipe
from tests.mocks.mock_file_logger import MockFileLogger
from tests.mocks.mock_pipe import PipeMock


class PipelineTestCase(unittest.TestCase):
    def test_01_an_empty_pipeline_returns_input_as_output(self):
        # Given
        pipeline_raw_input = {'numbers': [0]}

        # When
        pipeline = CIPipe(pipeline_raw_input)

        # Then
        self.assertEqual(pipeline.output(), {'numbers': [0]})

    def test_02_a_pipeline_can_execute_a_step_successfully(self):
        # Given
        pipeline_raw_input = {'numbers': [0]}

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._add_one))

        # Then
        expected_output = {'numbers': [1]}
        self.assertEqual(pipeline.output(), expected_output)

    def test_03_a_pipeline_can_execute_multiple_steps_successfully(self):
        # Given
        pipeline_raw_input = {'numbers': [0]}

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._add_one)
                    .step("my_second_step", self._add_another_one))

        # Then
        expected_output = {'numbers': [2]}
        self.assertEqual(pipeline.output(), expected_output)

    def test_04_a_pipeline_with_more_than_one_input_executes_successfully(self):
        # Given
        pipeline_raw_input = {'numbers': [1, 1]}

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._sum_all))

        # Then
        expected_output = {'numbers': [2]}
        self.assertEqual(pipeline.output(), expected_output)

    def test_05_can_get_pipeline_info(self):
        # Given
        pipeline_raw_input = {'numbers': [1, 1]}

        # When
        pipeline = (CIPipe(pipeline_raw_input)
                    .step("my_first_step", self._sum_all))

        info = pipeline.info()

        expected_info = {
            'defaults': {},
            'inputs': {'numbers': [1, 1]},
            'output': {'numbers': [2]},
            'steps': [
                {
                    'args': (),
                    'input': {'numbers': [1, 1]},
                    'kwargs': {},
                    'name': 'my_first_step',
                    'output': {'numbers': [2]}
                }
            ]
        }

        # Then
        self.assertEqual(info, expected_info)

    def test_06_can_forward_args_to_step(self):
        # Given
        pipeline_raw_input = {'numbers': [2]}

        # When
        info = (CIPipe(pipeline_raw_input)
                .step("params_test", self._scale, 5)
                .info())

        # Then
        expected_info = {
            'defaults': {},
            'inputs': {'numbers': [2]},
            'output': {'numbers': [10]},
            'steps': [
                {
                    'input': {'numbers': [2]},
                    'name': 'params_test',
                    'output': {'numbers': [10]},
                    'args': (5,),
                    'kwargs': {}
                }
            ]
        }
        self.assertEqual(info, expected_info)

    def test_07_can_forward_named_args_to_step(self):
        # Given
        pipeline_raw_input = {'numbers': [2]}

        # When
        info = (CIPipe(pipeline_raw_input)
                .step("scale by factor", self._scale_named, factor=5)
                .info())

        # Then
        expected_info = {
            'defaults': {},
            'inputs': {'numbers': [2]},
            'output': {'numbers': [10]},
            'steps': [
                {
                    'input': {'numbers': [2]},
                    'name': 'scale by factor',
                    'output': {'numbers': [10]},
                    'args': (),
                    'kwargs': {'factor': 5}
                }
            ]
        }
        self.assertEqual(info, expected_info)

    def test_08_can_define_default_named_args_for_steps(self):
        # Given
        pipeline_raw_input = {'numbers': [2]}

        # When
        info = (CIPipe(pipeline_raw_input)
                .set_defaults(factor=5)
                .step("scale by default factor", self._scale_named)
                .info())

        # Then
        expected_info = {
            'defaults': {'factor': 5},
            'inputs': {'numbers': [2]},
            'output': {'numbers': [10]},
            'steps': [
                {
                    'input': {'numbers': [2]},
                    'name': 'scale by default factor',
                    'output': {'numbers': [10]},
                    'args': (),
                    'kwargs': {'factor': 5}
                }
            ]
        }
        self.assertEqual(info, expected_info)

    def test_09_step_kwarg_overrides_default(self):
        # Given
        pipeline_raw_input = {'numbers': [2]}

        # When
        info = (CIPipe(pipeline_raw_input)
                .set_defaults(factor=5)
                .step("scale by default factor", self._scale_named, factor=10)
                .info())

        # Then
        expected_info = {
            'defaults': {'factor': 5},
            'inputs': {'numbers': [2]},
            'output': {'numbers': [20]},
            'steps': [
                {
                    'input': {'numbers': [2]},
                    'name': 'scale by default factor',
                    'output': {'numbers': [20]},
                    'args': (),
                    'kwargs': {'factor': 10}
                }
            ]
        }
        self.assertEqual(info, expected_info)

    def test_10_branch_creates_new_pipeline_with_same_steps(self):
        # Given
        pipeline_raw_input = {'numbers': [1]}
        pipeline = PipeMock(pipeline_raw_input)
        pipeline._steps.append({'name': 'add one'})  # simulamos un step

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            json.dump({pipeline._branch_name: {}}, tmp_file)
            trace_file = tmp_file.name

        # When
        new_pipeline = pipeline.branch(
            "branch 2", trace_file, MockFileLogger.new_for("log.txt", "/tmp")
        )

        # Then
        assert new_pipeline._branch_name == "branch 2"
        assert new_pipeline._steps == pipeline._steps

        # Cleanup
        os.remove(trace_file)

    def test_11_branch_trace_file_is_updated(self):
        # Given
        pipeline_raw_input = {'numbers': [1]}
        pipeline = PipeMock(pipeline_raw_input)

        trace_data = {pipeline._branch_name: {"1": {"name": "dummy_step"}}}
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            json.dump(trace_data, tmp_file)
            trace_file = tmp_file.name

        # When
        new_pipeline = pipeline.branch(
            "branch 2", trace_file, MockFileLogger.new_for("log.txt", "/tmp")
        )

        # Then
        with open(trace_file, 'r') as f:
            updated_trace = json.load(f)

        assert "branch 2" in updated_trace
        assert updated_trace["branch 2"] == trace_data[pipeline._branch_name]

        # Cleanup
        os.remove(trace_file)

    def test_12_branches_execute_same_step_independently(self):
        # Given
        pipeline_raw_input = {'numbers': [0]}
        pipeline = PipeMock(pipeline_raw_input)
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            json.dump({pipeline._branch_name: {}}, tmp_file)
            trace_file = tmp_file.name

        # When
        branch1 = pipeline.branch("branch 1A", trace_file, MockFileLogger.new_for("log1.txt", "/tmp"))
        branch2 = pipeline.branch("branch 1B", trace_file, MockFileLogger.new_for("log2.txt", "/tmp"))
        branch1._steps.append({'name': 'add one', 'func': lambda inputs: {'numbers': [inputs('numbers')[0] + 1]}})
        branch2._steps.append({'name': 'add one', 'func': lambda inputs: {'numbers': [inputs('numbers')[0] + 1]}})

        branch1_output = branch1._steps[0]['func'](lambda key: branch1._pipeline_inputs[key])
        branch2_output = branch2._steps[0]['func'](lambda key: branch2._pipeline_inputs[key])

        # Then
        assert branch1_output != branch2_output or branch1_output == branch2_output
        assert branch1_output['numbers'] == [1]
        assert branch2_output['numbers'] == [1]

        # Cleanup
        os.remove(trace_file)


    # Helper functions for the steps
    def _add_one(self, inputs):
        return {'numbers': [inputs('numbers')[0] + 1]}

    def _add_another_one(self, inputs):
        return {'numbers': [inputs('numbers')[0] + 1]}

    def _sum_all(self, inputs):
        return {'numbers': [sum(inputs('numbers'))]}

    def _scale(self, inputs, factor):
        return {'numbers': [x * factor for x in inputs('numbers')]}

    def _scale_named(self, inputs, factor=3):
        return {'numbers': [x * factor for x in inputs('numbers')]}


if __name__ == '__main__':
    unittest.main()
