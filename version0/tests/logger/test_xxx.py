import unittest

from isx_pipeline.isx_pipeline import ISXPipeline
from tests.mocks.mock_file_logger import MockFileLogger

class MockedISX:
    def preprocess(self, input_file, output_file):
        pass

    def spatial_filter(self, input_file, output_file, low_cutoff, high_cutoff):
        pass

    def make_output_file_paths(self, input_file, output_directory, suffix):
        pass

    def project_movie(self, input_files, output_file, stat_type):
        pass

    def motion_correct(self, input_files, output_files, max_translation, reference_file_name, output_translation_files, output_crop_rect_file):
        pass

    def dff(self, input_file, output_file, window_size, percentile):
        pass

    def pca_ica(self, input_file, output_file, num_components, num_cells, block_size):
        pass

    def event_detection(self, input_file, output_file, threshold):
        pass

    def auto_accept_reject(self, input_file, output_file, max_fpr, max_fnr):
        pass




class MyTestCase(unittest.TestCase):
    def setUp(self):
        self._logger = MockFileLogger.new_for("test_01.json", "logs")
        self._mocked_isx = MockedISX()

    def test_pipeline_does_not_execute_any_algorithm_if_there_is_no_data_to_run(self):
        empty_input_directory = "empty_directory"
        isx_pipeline = self._build_pipeline_with(empty_input_directory)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_not_executed(logged_data, "Preprocess Videos")

    def test_pipeline_executes_algorithm_if_there_is_data_to_run(self):
        input_directory = "videos"
        isx_pipeline = self._build_pipeline_with(input_directory)

        isx_pipeline.preprocess_videos()

        logged_data = isx_pipeline.trace()
        self._assert_algorithm_was_executed(logged_data, "Preprocess Videos")

    def test_pipeline_can_execute_multiple_algorithms_and_keep_trace_of_their_results(self):
        input_directory = "videos"
        isx_pipeline = self._build_pipeline_with(input_directory)

        (isx_pipeline
         .preprocess_videos()
         .bandpass_filter_videos()
         .motion_correction_videos()
         .normalize_dff_videos()
         .extract_neurons_pca_ica())

        logged_data = isx_pipeline.trace()
        print(logged_data.as_json())
        # self._assert_algorithm_was_executed(logged_data, "Extract Neurons PCA ICA")

    def _build_pipeline_with(self, input_directory):
        return ISXPipeline.new(self._mocked_isx, input_directory, self._logger)

    def _assert_algorithm_was_executed(self, logged_data, step_name):
        algorithms_executed = list(logged_data.as_json().keys())
        algorithm_execution_name = list(logged_data.as_json().values())[0].get("algorithm", None)
        algorithm_execution_output = list(logged_data.as_json().values())[0].get("output", None)
        self.assertEqual(len(algorithms_executed), 1)
        self.assertEqual(algorithm_execution_name, step_name)
        self.assertNotEquals(algorithm_execution_output, [])

    def _assert_algorithm_was_not_executed(self, logged_data, step_name):
        algorithms_executed = list(logged_data.as_json().keys())
        algorithm_execution_name = list(logged_data.as_json().values())[0].get("algorithm", None)
        algorithm_execution_output = list(logged_data.as_json().values())[0].get("output", None)
        self.assertEqual(len(algorithms_executed), 1)
        self.assertEqual(algorithm_execution_name, step_name)
        self.assertEqual(algorithm_execution_output, [])


if __name__ == '__main__':
    unittest.main()
