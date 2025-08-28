import unittest

from isx_pipeline.isx_pipeline import ISXPipeline
from logger.file_logger import FileLogger


class ISXFileLoggerPipelineIntegrationTests(unittest.TestCase):
    def test_pipeline_keeps_trace_with_file_logger(self):
        logger = FileLogger.new_for("test_01.json", "logs")
        isx_pipeline = ISXPipeline.new("videos", logger)

        self._execute_many_steps(isx_pipeline)

        self.assertTrue(self._expected_response())

    def test_pipeline_throws_error_if_workflow_continuation_is_attempted_with_different_input_directory(self):
        input_directory = "videos"
        output_directory = "logs"
        logger = FileLogger.new_for("test_01.json", output_directory)
        isx_pipeline = ISXPipeline.new(
            input_directory,
            logger,
        )

        isx_pipeline.preprocess_videos()

        different_input_directory = "invalid"

        with self.assertRaises(ValueError) as result:
            ISXPipeline.new(
                different_input_directory,
                logger,
            )
        error_message = result.exception.args[0]
        self.assertEqual(error_message, ISXPipeline.INVALID_INPUT_DIRECTORY_ERROR)

    def test_pipeline_can_continue_workflow_execution_if_same_input_and_output_directory_are_provided(self):
        input_directory = "videos"
        output_directory = "logs"
        logger = FileLogger.new_for("test_01.json", output_directory)
        isx_pipeline = ISXPipeline.new(
            input_directory,
            logger,
        )

        isx_pipeline.preprocess_videos()

        another_isx_pipeline = ISXPipeline.new(
            input_directory,
            logger,
        )

        (another_isx_pipeline
         .bandpass_filter_videos()
         .motion_correction_videos()
         .normalize_dff_videos()
         .extract_neurons_pca_ica()
         .detect_events_in_cells()
         .auto_accept_reject_cells()

         )

        print(another_isx_pipeline.trace())

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

    def _expected_response(self):
        # TODO: Assert expected response for given steps
        return True


if __name__ == '__main__':
    unittest.main()
