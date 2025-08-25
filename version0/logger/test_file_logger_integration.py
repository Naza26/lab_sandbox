import unittest

from isx_pipeline.isx_pipeline import ISXPipeline
from logger.file_logger import FileLogger


class FileLoggerPipelineIntegrationTests(unittest.TestCase):
    def test_pipeline_keeps_trace_with_file_logger(self):
        logger = FileLogger.new_for("test_01.json", "logs")
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
