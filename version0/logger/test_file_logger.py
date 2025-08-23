import unittest

from isx_pipeline.isx_pipeline import ISXPipeline
from logger.file_logger import FileLogger
from logger.mock_file_logger import MockFileLogger


class FileLoggerTests(unittest.TestCase):
    def test_file_logger_creates_empty_log_file(self):
        file_logger = MockFileLogger.new_for("../test_01", "logs")
        self.assertTrue(file_logger.is_empty())

    def test_file_logger_can_add_log(self):
        file_logger = MockFileLogger.new_for("../test_01", "logs")
        mocked_object = {"key": "value"}
        file_logger.add_log(mocked_object)
        self.assertFalse(file_logger.is_empty())
        logged_json_data = file_logger.all_logs_as_json()
        self.assertTrue(logged_json_data == mocked_object)

class MyTestCase(unittest.TestCase):
    def test_pipeline_keeps_trace_with_file_logger(self):
        logger = FileLogger.new_for("../test_01", "logs")
        isx_pipeline = ISXPipeline.new("videos", "output", logger)
        print(isx_pipeline.trace())
        self._execute_many_steps(isx_pipeline)
        print(isx_pipeline.trace())

    def _execute_many_steps(self, isx_pipeline):
        (
            isx_pipeline
            .preprocess_videos()
            .bandpass_filter_videos()
            .motion_correction_videos()
            .normalize_dff_videos()
            .extract_neurons_pca_ica()
            .detect_events_in_cells()
            .auto_accept_reject_cells()
        )


if __name__ == '__main__':
    unittest.main()
