from ci_pipe.pipeline import CIPipe
from ci_pipe.trace_builder import TraceBuilder


class MockedISXResult:
    pass


class MockedISXPipeline(CIPipe):
    INVALID_INPUT_DIRECTORY_ERROR = "Cannot create new pipeline with different input data in already created output directory"

    def __init__(self, inputs, logger):
        super().__init__(inputs)
        self._logger = logger
        self._output_folder = self._logger.directory()
        self._steps = []
        self._completed_step_names = set()
        if not self._logger.is_empty():
            self._steps = TraceBuilder.build_steps_from_trace(self._logger.read_json_from_file())
            self._completed_step_names = set(step.info()["name"] for step in self._steps)

    @classmethod
    def new(cls, input_directory, logger):
        inputs = cls._scan_files(input_directory)
        return cls(inputs, logger)

    @classmethod
    def _scan_files(cls, input_folder: str):
        return {"videos": []}

    def step(self, step_name, step_function, *args):
        mocked_isx_result = MockedISXResult()
        trace = TraceBuilder.build_dictionary_trace_from(self._steps)
        self._logger.write_json_to_file(trace)
        self._logger.add_log(trace)
        self._completed_step_names.add(step_name)
        return mocked_isx_result

    def trace(self):
        return self._logger.read_json_from_file()

    def preprocess_videos(self, name="Preprocess Videos"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def bandpass_filter_videos(self, name="Bandpass Filter Videos"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def normalize_dff_videos(self, name="Normalize dF/F Videos"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def detect_events_in_cells(self, name="Detect Events in Cells"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))

    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells"):
        def wrapped_step(input):
            pass

        return self.step(name, lambda input: wrapped_step(input))
