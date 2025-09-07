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
        self.assertTrue(logged_data.as_json() == {})

    def test_pipeline_executes_algorithm_if_there_is_data_to_run(self):
        input_directory = "videos"
        logger = MockFileLogger.new_for("test_01.json", "logs")
        isx_pipeline = MockedISXPipeline.new(input_directory, logger)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self.assertTrue(logged_data.as_json() != {})



if __name__ == '__main__':
    unittest.main()
