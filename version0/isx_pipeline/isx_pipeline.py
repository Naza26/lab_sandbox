import os
from ..ci_pipe.pipeline import CIPipe
import json
import shutil

class ISXPipeline(CIPipe):
    def __init__(self, isx, output_folder, inputs, branch_name="branch 1"):
        super().__init__(inputs)
        self._isx = isx
        self._steps = []
        self.branch_name = branch_name
        self._output_folder, self._trace_file = self._create_output_folder(output_folder)

    @classmethod
    def new(cls, isx, input_folder, output_folder="output", branch_name="branch 1"):
        inputs = cls._scan_files(input_folder)
        return cls(isx, output_folder, inputs, branch_name)
    
    def branch(self, branch_name):
        new_pipeline = ISXPipeline(
            isx=self._isx,
            output_folder=self._output_folder,
            inputs=self._pipeline_inputs,
            branch_name=branch_name
        )
        with open(self._trace_file, "r") as f:
            trace = json.load(f)

        if self.branch_name in trace:
            base_branch_trace = trace[self.branch_name]
            trace[branch_name] = dict(base_branch_trace)
            with open(self._trace_file, "w") as f:
                json.dump(trace, f, indent=4)

        new_pipeline._steps = list(self._steps)
        return new_pipeline


    @classmethod
    def _scan_files(self , input_folder: str):
        files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.isxd')]
        return { "videos": files }
    
    def step(self, step_name, step_function, *args):
        step_folder_path = self._step_folder_path(step_name)
        os.makedirs(step_folder_path, exist_ok=True)

        result = super().step(step_name, step_function, *args)
        self._update_trace()

        return result

    def trace(self):
        with open(self._trace_file, "r") as f:
            trace = json.load(f)
        branch_trace = trace.get(self.branch_name, {})
        return {
            "branch_name": self.branch_name,
            "steps": branch_trace
        }

    def preprocess_videos(self, name="Preprocess Videos"):        
        def wrapped_step(input):
            input_videos, pp_files = self._input_and_output_files(input, 'videos', name, 'PP')
            self._isx.preprocess(input_videos, pp_files)
            return { 'videos': pp_files }

        return self.step(name, lambda input: wrapped_step(input))

    def bandpass_filter_videos(self, name="Bandpass Filter Videos"):
        def wrapped_step(input):
            input_videos, bp_files = self._input_and_output_files(input, 'videos', name, 'BP')
            self._isx.spatial_filter(input_videos, bp_files, low_cutoff=0.005, high_cutoff=0.5)
            return { 'videos': bp_files }

        return self.step(name, lambda input: wrapped_step(input))
    
    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series"):
        def wrapped_step(input):
            input_videos, mc_files = self._input_and_output_files(input, 'videos', name, 'MC')
            step_folder = self._step_folder_path(name)
            translation_files = self._isx.make_output_file_paths(mc_files, step_folder, 'translations', 'csv')
            mean_proj_file = os.path.join(step_folder, f'{series_name}-mean_image.isxd')
            crop_rect_file = os.path.join(step_folder, f'{series_name}-crop_rect.csv')
            self._isx.project_movie(input_videos, mean_proj_file, stat_type='mean')
            self._isx.motion_correct(input_videos, mc_files, max_translation=20, reference_file_name=mean_proj_file,
                                      output_translation_files=translation_files, output_crop_rect_file=crop_rect_file)
            return { 'videos': mc_files, 'translations': translation_files, 'crop_rect': [crop_rect_file], 'mean_projection': [mean_proj_file] }

        return self.step(name, lambda input: wrapped_step(input))

    def normalize_dff_videos(self, name="Normalize dF/F Videos"):
        def wrapped_step(input):
            input_videos, dff_files = self._input_and_output_files(input, 'videos', name, 'DFF')
            self._isx.dff(input_videos, dff_files, f0_type='mean')
            return { 'videos': dff_files }

        return self.step(name, lambda input: wrapped_step(input))
    
    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA"):
        def wrapped_step(input):
            input_videos, ic_files = self._input_and_output_files(input, 'videos', name, 'PCA-ICA')
            self._isx.pca_ica(input_videos, ic_files, 180, int(1.15 * 180), block_size=1000)
            return { 'cellsets': ic_files }

        return self.step(name, lambda input: wrapped_step(input))
    
    def detect_events_in_cells(self, name="Detect Events in Cells"):
        def wrapped_step(input):
            input_cellsets, event_files = self._input_and_output_files(input, 'cellsets', name, 'ED')
            self._isx.event_detection(input_cellsets, event_files, threshold=5)
            return { 'events': event_files }

        return self.step(name, lambda input: wrapped_step(input))

    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells"):
        def wrapped_step(input):
            input_cellsets = input('cellsets')
            copied_cellsets = self._copy_files_to_step_folder(input_cellsets, name)
            input_events = input('events')
            filters = [('SNR', '>', 3), ('Event Rate', '>', 0), ('# Comps', '=', 1)]
            self._isx.auto_accept_reject(copied_cellsets, input_events, filters)
            return { 'cellsets': copied_cellsets }

        return self.step(name, lambda input: wrapped_step(input))

    def _create_output_folder(self, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        trace_path = os.path.join(output_folder, "trace.json")
        if not os.path.exists(trace_path):
            with open(trace_path, 'w') as f:
                f.write("{}")
        return output_folder, trace_path

    def _step_folder_path(self, step_name):
        with open(self._trace_file, "r") as f:
            trace = json.load(f)
        
        branch_trace = trace.get(self.branch_name, {})
        step_index = len(branch_trace) + 1

        step_folder_name = f"{self.branch_name} - step {step_index} - {step_name}"
        return os.path.join(self._output_folder, step_folder_name)


    def _update_trace(self):
        step_info = self._steps[-1].info()
        with open(self._trace_file, "r") as f:
            trace = json.load(f)
        if self.branch_name not in trace:
            trace[self.branch_name] = {}
        self._add_step_to_trace(step_info, trace[self.branch_name])

        with open(self._trace_file, "w") as f:
            json.dump(trace, f, indent=4)

    def _add_step_to_trace(self, step_info, branch_trace):
        step_number = str(len(branch_trace) + 1)
        branch_trace[step_number] = {
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
            dest = os.path.join(step_folder, os.path.basename(file))
            shutil.copy2(file, dest)
            copied_files.append(dest)
        return copied_files