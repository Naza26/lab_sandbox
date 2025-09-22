import os
import shutil

from ci_pipe.pipeline import CIPipe
from ci_pipe.plotter import Plotter
from ci_pipe.trace_builder import TraceBuilder
from isx_pipeline.available_isx_algorithms import AvailableISXAlgorithms
from isx_pipeline.config.isx_config import ISXConfig
from utils import build_filesystem_path_from, create_directory_from, list_directory_contents, last_part_of_path, \
    is_content_available_in


class ISXPipeline(CIPipe):
    INVALID_INPUT_DIRECTORY_ERROR = "Cannot create new pipeline with different input data in already created output directory"

    def __init__(self, isx, inputs, logger, branch_name = "branch 1"):
        super().__init__(inputs, branch_name)
        self._isx = isx
        self._logger = logger
        self._completed_step_names = set()
        self.available_algorithms = AvailableISXAlgorithms
        self._config = ISXConfig()
        self._plotter = Plotter()
        if not self._logger.is_empty():
            self._steps = TraceBuilder.build_steps_from_trace(self._logger.read_json_from_file(), self._branch_name)
            self._completed_step_names = set(step.name() for step in self._steps)

    @classmethod
    def new(cls, isx, input_directory, logger, branch_name = "branch 1"):
        if not is_content_available_in(input_directory) and is_content_available_in(logger.directory()):
            raise ValueError(cls.INVALID_INPUT_DIRECTORY_ERROR)
        inputs = cls._scan_files(input_directory)
        return cls(isx, inputs, logger, branch_name)
    
    def branch(self, branch_name):
        new_pipe = super().branch(branch_name)
        new_pipe.__class__ = ISXPipeline
        new_pipe._isx = self._isx
        new_pipe._logger = self._logger
        new_pipe._completed_step_names = set(self._completed_step_names)
        new_pipe.available_algorithms = self.available_algorithms
        new_pipe._config = self._config
        new_pipe._plotter = self._plotter
        return new_pipe
    
    def info(self, step_number):
        self._plotter.get_step_info(self._logger.read_json_from_file(), step_number, self._branch_name)

    def trace(self):
        self._plotter.get_all_trace_from_branch(self._logger.read_json_from_file(), self._branch_name)

    def show(self):
        self._plotter.get_all_trace(self._logger.read_json_from_file(), self._branch_name)

    @classmethod
    def _scan_files(cls, input_folder: str):
        files = [
            build_filesystem_path_from(input_folder, f) for f in list_directory_contents(input_folder) if
            f.endswith('.isxd')]
        return {"videos": files}

    def step(self, step_name, step_function, *args, **kwargs):
        if step_name in self._completed_step_names:
            return None
        step_folder_path = self._step_folder_path(step_name)
        create_directory_from(step_folder_path)

        result = super().step(step_name, step_function, *args, **kwargs)
        self._update_trace()
        self._completed_step_names.add(step_name)
        return result


    def _step_folder_path(self, step_name):
        steps_count = len(self._steps)
        step_folder_name = f"{self._branch_name}: step {steps_count + 1} - {step_name}"
        return build_filesystem_path_from(self._logger.directory(), step_folder_name)


    def _update_trace(self):
        all_trace = self._logger.read_json_from_file() or {}
        all_trace[self._branch_name] = TraceBuilder.build_dictionary_trace_from(self._steps)
        self._logger.write_json_to_file(all_trace)

    def _input_and_output_files(self, input, input_key, step_name, output_suffix):
        input_files = input(input_key)
        step_folder = self._step_folder_path(step_name)
        input_output_pairs = []
        for in_file in input_files:
            out_file = self._isx.make_output_file_paths([in_file], step_folder, output_suffix)[0]
            input_output_pairs.append((in_file, out_file))
        return input_output_pairs

    def _process_input_output_pairs(self, input_output_pairs, fn):
        for in_file, out_file in input_output_pairs:
            fn([in_file], [out_file])

    def _basename_no_ext(self, path):
        return os.path.splitext(os.path.basename(path))[0]

    def _match_events_to_cellsets(self, cellsets, events):
        # This is temporary, we will persist the correspondent inputs so we don't have to match them manually
        # Exact prefix match: event basename must be f"{cellset_basename}-ED"
        event_by_base = {self._basename_no_ext(ev): ev for ev in events}
        matches = {}
        unmatched_cellsets = []
        for cs in cellsets:
            cs_base = self._basename_no_ext(cs)
            expected_event_base = f"{cs_base}-ED"
            ev = event_by_base.get(expected_event_base)
            if ev:
                matches[cs] = ev
            else:
                unmatched_cellsets.append(cs)
        used_events = set(matches.values())
        unmatched_events = [ev for ev in events if ev not in used_events]
        if unmatched_cellsets:
            print("[auto_accept_reject] UNMATCHED CELLSETS:")
            for cs in unmatched_cellsets:
                print(f"  - {os.path.basename(cs)}")
        if unmatched_events:
            print("[auto_accept_reject] UNMATCHED EVENTS:")
            for ev in unmatched_events:
                print(f"  - {os.path.basename(ev)}")
        return matches

    def _copy_files_to_step_folder(self, files, step_name):
        step_folder = self._step_folder_path(step_name)
        copied_files = []
        for file in files:
            dest = build_filesystem_path_from(step_folder, last_part_of_path(file))
            shutil.copy2(file, dest)
            copied_files.append(dest)
        return copied_files


# ===============================
#         ISX ALGORITHMS
# ===============================

    def preprocess_videos(self, name="Preprocess Videos"):
        parameters = self._config.get_parameters(self.available_algorithms.PREPROCESS_VIDEOS.value)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PP')
            self._process_input_output_pairs(input_output_pairs, self._isx.preprocess)
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, wrapped_step, **parameters)

    def bandpass_filter_videos(self, name="Bandpass Filter Videos", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.BANDPASS_FILTER_VIDEOS.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'BP')
            self._process_input_output_pairs(
                 input_output_pairs,
                 lambda i, o: self._isx.spatial_filter(
                    i, o,
                    low_cutoff=parameters['low_cutoff'],
                    high_cutoff=parameters['high_cutoff']
                )
            )
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, wrapped_step, **parameters)
        
    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.MOTION_CORRECTION_VIDEOS.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'MC')
            step_folder = self._step_folder_path(name)
            mc_files = []
            translation_files = []
            mean_proj_files = []
            crop_rect_files = []
            for in_file, out_file in input_output_pairs:
                video_name = os.path.splitext(os.path.basename(in_file))[0]
                mean_proj_file = os.path.join(step_folder, f'{video_name}-{series_name}-mean_image.isxd')
                crop_rect_file = os.path.join(step_folder, f'{video_name}-{series_name}-crop_rect.csv')
                translation_file = self._isx.make_output_file_paths([out_file], step_folder, 'translations', 'csv')[0]
                self._isx.project_movie([in_file], mean_proj_file, stat_type=parameters['stat_type'])
                self._isx.motion_correct(
                    [in_file],
                    [out_file],
                    max_translation=parameters['max_translation'],
                    reference_file_name=mean_proj_file,
                    output_translation_files=[translation_file],
                    output_crop_rect_file=crop_rect_file
                )
                mc_files.append(out_file)
                translation_files.append(translation_file)
                mean_proj_files.append(mean_proj_file)
                crop_rect_files.append(crop_rect_file)
            return {'videos': mc_files, 'translations': translation_files, 'crop_rect': crop_rect_files,
                    'mean_projection': mean_proj_files}

        return self.step(name, wrapped_step, **parameters)


    def normalize_dff_videos(self, name="Normalize dF/F Videos", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.NORMALIZE_DFF_VIDEOS.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'DFF')
            self._process_input_output_pairs(
                input_output_pairs,
                lambda i, o: self._isx.dff(i, o, f0_type=parameters['f0_type'])
            )
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, wrapped_step, **parameters)


    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.EXTRACT_NEURONS_PCA_ICA.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PCA-ICA')
            cellsets = []

            def pca_ica_fn(i, o):
                self._isx.pca_ica(
                    i,
                    o,
                    parameters['num_components'],
                    parameters['num_iterations'],
                    block_size=parameters['block_size']
                )
                cellsets.append(o[0])

            self._process_input_output_pairs(input_output_pairs, pca_ica_fn)
            return {'cellsets': cellsets}

        return self.step(name, wrapped_step, **parameters)


    def detect_events_in_cells(self, name="Detect Events in Cells", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.DETECT_EVENTS_IN_CELLS.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_output_pairs = self._input_and_output_files(input, 'cellsets', name, 'ED')
            events = []

            def event_fn(i, o):
                self._isx.event_detection(i, o, threshold=parameters['threshold'])
                events.append(o[0])

            self._process_input_output_pairs(input_output_pairs, event_fn)
            return {'events': events}

        return self.step(name, wrapped_step, **parameters)


    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells", **kwargs):
        parameters = self._config.get_parameters(self.available_algorithms.AUTO_ACCEPT_REJECT_CELLS.value, **kwargs)
        def wrapped_step(input, **parameters):
            input_cellsets = input('cellsets')
            copied_cellsets = self._copy_files_to_step_folder(input_cellsets, name)
            input_events = input('events')
            filters = parameters['filters']
            matches = self._match_events_to_cellsets(copied_cellsets, input_events)
            for cellset, event_file in matches.items():
                print(f"[auto_accept_reject] MATCH: {os.path.basename(cellset)} -> {os.path.basename(event_file)}")
                self._isx.auto_accept_reject([cellset], [event_file], filters)
            return {'cellsets': copied_cellsets}

        return self.step(name, wrapped_step, **parameters)