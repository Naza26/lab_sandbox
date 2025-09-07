import unittest

from isx_pipeline.mocked_isx_pipeline import MockedISXPipeline
from tests.mocks.mock_file_logger import MockFileLogger


class MyTestCase(unittest.TestCase):
    def test_pipeline_does_not_execute_any_algorithm_if_there_is_no_data_to_run(self):
        empty_input_directory = "empty_directory"
        logger = MockFileLogger.new_for("test_01.json", "logs")
        isx_pipeline = MockedISXPipeline.new(empty_input_directory, logger)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_not_executed(logged_data, "Preprocess Videos")

    def test_pipeline_executes_algorithm_if_there_is_data_to_run(self):
        input_directory = "videos"
        logger = MockFileLogger.new_for("test_01.json", "logs")
        isx_pipeline = MockedISXPipeline.new(input_directory, logger)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_executed(logged_data, "Preprocess Videos")

    def _assert_algorithm_was_executed(self, logged_data, step_name):
        algorithms_executed = list(logged_data.as_json().keys())
        algorithm_execution_name = list(logged_data.as_json().values())[0].get("algorithm", None)
        algorithm_execution_output = list(logged_data.as_json().values())[0].get("output", None)
        self.assertEqual(len(algorithms_executed), 1)
        self.assertEqual(algorithm_execution_name, step_name)
        self.assertNotEquals(algorithm_execution_output,[])

    def _assert_algorithm_was_not_executed(self, logged_data, step_name):
        algorithms_executed = list(logged_data.as_json().keys())
        algorithm_execution_name = list(logged_data.as_json().values())[0].get("algorithm", None)
        algorithm_execution_output = list(logged_data.as_json().values())[0].get("output", None)
        self.assertEqual(len(algorithms_executed), 1)
        self.assertEqual(algorithm_execution_name, step_name)
        self.assertEqual(algorithm_execution_output,[])



if __name__ == '__main__':
    unittest.main()
