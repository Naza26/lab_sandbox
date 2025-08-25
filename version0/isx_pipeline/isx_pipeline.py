import importlib
import shutil
from typing import ClassVar, Any

from ci_pipe.pipeline import CIPipe
from utils import build_filesystem_path_from, create_directory_from, list_directory_contents, last_part_of_path


class ISXPipeline(CIPipe):
    isx_package: ClassVar[Any] = importlib.import_module("isx")

    def __init__(self, output_folder, inputs, logger):
        super().__init__(inputs)
        self._isx = self.__class__.isx_package
        self._steps = []
        self._logger = logger
        self._output_folder = self._logger.directory()

    @classmethod
    def new(cls, input_folder, output_folder, logger):
        inputs = cls._scan_files(input_folder)
        return cls(output_folder, inputs, logger)

    @classmethod
    def _scan_files(cls, input_folder: str):
        files = [
            build_filesystem_path_from(input_folder, f) for f in list_directory_contents(input_folder) if f.endswith('.isxd')]
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
            input_videos, pp_files = self._input_and_output_files(input, 'videos', name, 'PP')
            self._isx.preprocess(input_videos, pp_files)
            return {'videos': pp_files}

        return self.step(name, lambda input: wrapped_step(input))

    def bandpass_filter_videos(self, name="Bandpass Filter Videos"):
        def wrapped_step(input):
            input_videos, bp_files = self._input_and_output_files(input, 'videos', name, 'BP')
            self._isx.spatial_filter(input_videos, bp_files, low_cutoff=0.005, high_cutoff=0.5)
            return {'videos': bp_files}

        return self.step(name, lambda input: wrapped_step(input))

    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series"):
        def wrapped_step(input):
            input_videos, mc_files = self._input_and_output_files(input, 'videos', name, 'MC')
            step_folder = self._step_folder_path(name)
            translation_files = self._isx.make_output_file_paths(mc_files, step_folder, 'translations', 'csv')
            mean_proj_file = build_filesystem_path_from(step_folder, f'{series_name}-mean_image.isxd')
            crop_rect_file = build_filesystem_path_from(step_folder, f'{series_name}-crop_rect.csv')
            self._isx.project_movie(input_videos, mean_proj_file, stat_type='mean')
            self._isx.motion_correct(input_videos, mc_files, max_translation=20, reference_file_name=mean_proj_file,
                                     output_translation_files=translation_files, output_crop_rect_file=crop_rect_file)
            return {'videos': mc_files, 'translations': translation_files, 'crop_rect': [crop_rect_file],
                    'mean_projection': [mean_proj_file]}

        return self.step(name, lambda input: wrapped_step(input))

    def normalize_dff_videos(self, name="Normalize dF/F Videos"):
        def wrapped_step(input):
            input_videos, dff_files = self._input_and_output_files(input, 'videos', name, 'DFF')
            self._isx.dff(input_videos, dff_files, f0_type='mean')
            return {'videos': dff_files}

        return self.step(name, lambda input: wrapped_step(input))

    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA"):
        def wrapped_step(input):
            input_videos, ic_files = self._input_and_output_files(input, 'videos', name, 'PCA-ICA')
            self._isx.pca_ica(input_videos, ic_files, 180, int(1.15 * 180), block_size=1000)
            return {'cellsets': ic_files}

        return self.step(name, lambda input: wrapped_step(input))

    def detect_events_in_cells(self, name="Detect Events in Cells"):
        def wrapped_step(input):
            input_cellsets, event_files = self._input_and_output_files(input, 'cellsets', name, 'ED')
            self._isx.event_detection(input_cellsets, event_files, threshold=5)
            return {'events': event_files}

        return self.step(name, lambda input: wrapped_step(input))

    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells"):
        def wrapped_step(input):
            input_cellsets = input('cellsets')
            copied_cellsets = self._copy_files_to_step_folder(input_cellsets, name)
            input_events = input('events')
            filters = [('SNR', '>', 3), ('Event Rate', '>', 0), ('# Comps', '=', 1)]
            self._isx.auto_accept_reject(copied_cellsets, input_events, filters)
            return {'cellsets': copied_cellsets}

        return self.step(name, lambda input: wrapped_step(input))

    def _step_folder_path(self, step_name):
        step_index = len(self._steps)
        step_folder_name = f"step {step_index + 1} - {step_name}"
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
        output_files = self._isx.make_output_file_paths(input_files, step_folder, output_suffix)
        return input_files, output_files

    def _copy_files_to_step_folder(self, files, step_name):
        step_folder = self._step_folder_path(step_name)
        copied_files = []
        for file in files:
            dest = build_filesystem_path_from(step_folder, last_part_of_path(file))
            shutil.copy2(file, dest)
            copied_files.append(dest)
        return copied_files
