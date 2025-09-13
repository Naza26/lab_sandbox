import unittest

from isx_pipeline.available_isx_algorithms import AvailableISXAlgorithms
from isx_pipeline.isx_pipeline import ISXPipeline
from tests.mocks.mock_file_logger import MockFileLogger
from tests.mocks.mock_isx import MockedISX


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self._logger = MockFileLogger.new_for("test_01.json", "logs")
        self._isx = MockedISX()

    def test_pipeline_does_not_execute_any_algorithm_if_there_is_no_data_to_run(self):
        empty_input_directory = "empty_directory"
        isx_pipeline = self._build_pipeline_with(empty_input_directory)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_not_executed(logged_data, AvailableISXAlgorithms.PREPROCESS_VIDEOS.value)

    def test_pipeline_executes_algorithm_if_there_is_data_to_run(self):
        input_directory = "videos"
        isx_pipeline = self._build_pipeline_with(input_directory)
        expected_ran_algorithms = [AvailableISXAlgorithms.PREPROCESS_VIDEOS.value]

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_executed(logged_data, expected_ran_algorithms)

    def test_pipeline_can_execute_multiple_algorithms_and_keep_trace_of_their_results(self):
        input_directory = "videos"
        isx_pipeline = self._build_pipeline_with(input_directory)
        expected_ran_algorithms = [
            AvailableISXAlgorithms.PREPROCESS_VIDEOS.value, AvailableISXAlgorithms.BANDPASS_FILTER_VIDEOS.value,
            AvailableISXAlgorithms.MOTION_CORRECTION_VIDEOS.value, AvailableISXAlgorithms.NORMALIZE_DFF_VIDEOS.value,
            AvailableISXAlgorithms.EXTRACT_NEURONS_PCA_ICA.value]

        (isx_pipeline
         .preprocess_videos()
         .bandpass_filter_videos()
         .motion_correction_videos()
         .normalize_dff_videos()
         .extract_neurons_pca_ica())

        logged_data = isx_pipeline.trace()
        print("Logged data:", logged_data.as_json())
        self._assert_algorithm_was_executed(logged_data, expected_ran_algorithms)

    def _build_pipeline_with(self, input_directory):
        return ISXPipeline.new(self._isx, input_directory, self._logger)

    def _assert_algorithm_was_executed(self, logged_data, expected_ran_algorithms):
        executed_algorithms = list(logged_data.as_json().values())
        if len(executed_algorithms) == 0:
            self.fail("No algorithms were executed")

        for executed_algorithm in executed_algorithms:
            algorithm_name = executed_algorithm.get("algorithm", None)
            algorithm_output = executed_algorithm.get("output", None)
            self.assertTrue(algorithm_name in expected_ran_algorithms)
            self.assertIsNotNone(algorithm_output)
            self.assertNotEqual(algorithm_output, [])

        self.assertEqual(len(executed_algorithms), len(expected_ran_algorithms))

    def _assert_algorithm_was_not_executed(self, logged_data, step_name):
        logged_json = logged_data.as_json()
        if logged_json and len(logged_json) > 0:
            algorithms_executed = list(logged_json.keys())
            algorithm_execution_name = list(logged_json.values())[0].get("algorithm", None)
            algorithm_execution_output = list(logged_json.values())[0].get("output", None)
            self.assertEqual(len(algorithms_executed), 1)
            self.assertEqual(algorithm_execution_name, step_name)
            self.assertEqual(algorithm_execution_output, [])
        else:
            # If no log data, it means no algorithm was executed (which is what we expect)
            pass


if __name__ == '__main__':
    unittest.main()
