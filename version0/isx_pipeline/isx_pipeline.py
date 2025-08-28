import importlib
import json
import os
import shutil
from typing import ClassVar, Any

from ci_pipe.pipeline import CIPipe
from utils import build_filesystem_path_from, create_directory_from, list_directory_contents, last_part_of_path, \
    is_content_available_in


class ISXPipeline(CIPipe):
    INVALID_INPUT_DIRECTORY_ERROR = "Cannot create new pipeline with different input data in already created output directory"
    isx_package: ClassVar[Any] = importlib.import_module("isx")

    def __init__(self, inputs, logger):
        super().__init__(inputs)
        self._isx = self.__class__.isx_package
        self._steps = []
        self._logger = logger
        self._output_folder = self._logger.directory()

    @classmethod
    def new(cls, input_directory, logger):
        if not is_content_available_in(input_directory) and is_content_available_in(logger.directory()):
            raise ValueError(cls.INVALID_INPUT_DIRECTORY_ERROR)
        inputs = cls._scan_files(input_directory)
        return cls(inputs, logger)

    @classmethod
    def _scan_files(cls, input_folder: str):
        files = [
            build_filesystem_path_from(input_folder, f) for f in list_directory_contents(input_folder) if
            f.endswith('.isxd')]
        return {"videos": files}

    def step(self, step_name, step_function, *args):
        step_folder_path = self._step_folder_path(step_name)
        create_directory_from(step_folder_path)

        result = super().step(step_name, step_function, *args)
        self._update_trace()

        return result

    def trace(self):
        self._logger.read_json_from_file()

    def preprocess_videos(self, name="Preprocess Videos"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PP')
            self._process_input_output_pairs(input_output_pairs, self._isx.preprocess)
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))

    def bandpass_filter_videos(self, name="Bandpass Filter Videos"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'BP')
            self._process_input_output_pairs(input_output_pairs, lambda i, o: self._isx.spatial_filter(i, o, low_cutoff=0.005, high_cutoff=0.5))
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))

    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series"):
        def wrapped_step(input):
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
                self._isx.project_movie([in_file], mean_proj_file, stat_type='mean')
                self._isx.motion_correct([in_file], [out_file], max_translation=20, reference_file_name=mean_proj_file,
                                     output_translation_files=[translation_file], output_crop_rect_file=crop_rect_file)
                mc_files.append(out_file)
                translation_files.append(translation_file)
                mean_proj_files.append(mean_proj_file)
                crop_rect_files.append(crop_rect_file)
            return {'videos': mc_files, 'translations': translation_files, 'crop_rect': crop_rect_files,
                    'mean_projection': mean_proj_files}

        return self.step(name, lambda input: wrapped_step(input))

    def normalize_dff_videos(self, name="Normalize dF/F Videos"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'DFF')
            self._process_input_output_pairs(input_output_pairs, lambda i, o: self._isx.dff(i, o, f0_type='mean'))
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))

    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PCA-ICA')
            cellsets = []
            def pca_ica_fn(i, o):
                self._isx.pca_ica(i, o, 180, int(1.15 * 180), block_size=1000)
                cellsets.append(o[0])
            self._process_input_output_pairs(input_output_pairs, pca_ica_fn)
            return {'cellsets': cellsets}

        return self.step(name, lambda input: wrapped_step(input))

    def detect_events_in_cells(self, name="Detect Events in Cells"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'cellsets', name, 'ED')
            events = []
            def event_fn(i, o):
                self._isx.event_detection(i, o, threshold=5)
                events.append(o[0])
            self._process_input_output_pairs(input_output_pairs, event_fn)
            return {'events': events}

        return self.step(name, lambda input: wrapped_step(input))

    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells"):
        def wrapped_step(input):
            input_cellsets = input('cellsets')
            copied_cellsets = self._copy_files_to_step_folder(input_cellsets, name)
            input_events = input('events')
            filters = [('SNR', '>', 3), ('Event Rate', '>', 0), ('# Comps', '=', 1)]
            matches = self._match_events_to_cellsets(copied_cellsets, input_events)
            for cellset, event_file in matches.items():
                print(f"[auto_accept_reject] MATCH: {os.path.basename(cellset)} -> {os.path.basename(event_file)}")
                self._isx.auto_accept_reject([cellset], [event_file], filters)
            return {'cellsets': copied_cellsets}

        return self.step(name, lambda input: wrapped_step(input))

    def _step_folder_path(self, step_name):
        steps = list(self._logger.read_json_from_file().keys())
        last_step_index_from_trace = int(steps[-1]) if steps else 0
        step_folder_name = f"step {last_step_index_from_trace + 1} - {step_name}"
        return build_filesystem_path_from(self._output_folder, step_folder_name)

    def _update_trace(self):
        step_info = self._steps[-1].info()
        trace = self._logger.read_json_from_file()
        self._add_step_to_trace(step_info, trace)
        self._logger.write_json_to_file(trace)

    def _add_step_to_trace(self, step_info, trace):
        step_number = str(len(self._steps))
        trace[step_number] = {
            "algorithm": step_info["name"],
            "input": [item for v in step_info["input"].values() for item in v],
            "output": [item for v in step_info["output"].values() for item in v]
        }

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
        event_by_base = { self._basename_no_ext(ev): ev for ev in events }
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
