import os
from ..ci_pipe.pipeline import CIPipe
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_output")

class ISXPipeline(CIPipe):
    def __init__(self, isx, output_folder, inputs):
        super().__init__(inputs)
        self._isx = isx
        self._steps = []
        self._output_folder, self._trace_file = self.create_output_folder(output_folder, inputs)

    @classmethod
    def new(cls, isx, input_folder, output_folder="output"):
        inputs = cls._scan_files(input_folder)
        return cls(isx, output_folder, inputs)

    def create_output_folder(self, output_folder, inputs):
        os.makedirs(output_folder, exist_ok=True)

        trace_path = os.path.join(output_folder, "trace.json")
        if not os.path.exists(trace_path):
            with open(trace_path, 'w') as f:
                f.write("{}")
        return output_folder, trace_path
    
    def step(self, step_name, step_function, *args):
        step_folder_path = self._step_folder_path(step_name)
        os.makedirs(step_folder_path, exist_ok=True)

        updated_args = []
        for arg in args:
            if isinstance(arg, list) and all(isinstance(x, str) for x in arg):
                new_paths = [os.path.join(step_folder_path, os.path.basename(p)) for p in arg]
                updated_args.append(new_paths)
            else:
                updated_args.append(arg)

        result = super().step(step_name, step_function, *updated_args)

        step_info = self._steps[-1].info()
        self._update_trace(step_info)

        return result
    
    def _step_folder_path(self, step_name):
        step_index = len(self._steps)
        step_folder_name = f"step {step_index + 1} - {step_name}"
        return os.path.join(self._output_folder, step_folder_name)

    def _update_trace(self, step_info):
        with open(self._trace_file, "r") as f:
            trace = json.load(f)

        def extract_paths(data):
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        return v
                return []
            elif isinstance(data, list):
                return data
            else:
                return []

        step_number = str(len(self._steps))

        trace[step_number] = {
            "algorithm": step_info["name"],
            "input": extract_paths(step_info["input"]),
            "output": extract_paths(step_info["output"])
        }

        with open(self._trace_file, "w") as f:
            json.dump(trace, f, indent=4)

    def trace(self):
        with open(self._trace_file, "r") as f:
            return json.load(f)


    @classmethod
    def _scan_files(self , input_folder: str):
        # Check existence
        files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.isxd')]
        return files

        # "preprocess_videos",
        # "bandpass_filter_videos",
        # "motion_correction_videos",

    def preprocess_videos(self, name="Preprocess Videos"):
        input_files = self.next_step_input()
        pp_files = self._isx.make_output_file_paths(input_files, self._step_folder_path(name), 'PP')
        return self.step(name, lambda files, pp: self._preprocess_result(files, pp), pp_files)

    def bandpass_filter_videos(self, name="Bandpass Filter Videos"):
        input_files = self.next_step_input()['videos']
        bp_files = self._isx.make_output_file_paths(input_files, self._step_folder_path(name), 'BP')
        return self.step(name, lambda files, bp: self._bandpass_filter_result(files, bp), bp_files)
    
    def motion_correction_videos(self, name="Motion Correction Videos", series_name="series"):
        input_files = self.next_step_input()['videos']
        step_folder = self._step_folder_path(name)
        mean_proj_file = os.path.join(step_folder, f'{series_name}-mean_image.isxd')
        mc_files = self._isx.make_output_file_paths(input_files, step_folder, 'MC')
        translation_files = self._isx.make_output_file_paths(mc_files, step_folder, 'translations', 'csv')
        crop_rect_file = os.path.join(step_folder, f'{series_name}-crop_rect.csv')
        return self.step(name, lambda files, mean_proj, mc, trans, crop: self._motion_correction_result(files, mean_proj, mc, trans, crop), mean_proj_file, mc_files, translation_files, crop_rect_file)

    def normalize_dff_videos(self, name="Normalize dF/F Videos"):
        input_files = self.next_step_input()['videos']
        dff_files = self._isx.make_output_file_paths(input_files, self._step_folder_path(name), 'DFF')
        return self.step(name, lambda files, dff: self._normalize_dff_result(files, dff), dff_files)
    
    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA"):
        input_files = self.next_step_input()['videos']
        ic_files = self._isx.make_output_file_paths(input_files, self._step_folder_path(name), 'PCA-ICA')
        return self.step(name, lambda files, ic: self._extract_neurons_pca_ica_result(files, ic), ic_files)
    
    def detect_events_in_cells(self, name="Detect Events in Cells"):
        input_files = self.next_step_input()['cellsets']
        event_files = self._isx.make_output_file_paths(input_files, self._step_folder_path(name), 'ED')
        return self.step(name, lambda files, events: self._detect_events_in_cells_result(files, events), event_files)

    def _preprocess_result(self, files, pp):
        self._isx.preprocess(files, pp)
        return { 'videos': pp }
    
    def _bandpass_filter_result(self, files, bp):
        self._isx.spatial_filter(files['videos'], bp, low_cutoff=0.005, high_cutoff=0.5)
        return { 'videos': bp }

    def _motion_correction_result(self, files, mean_proj, mc, trans, crop):
        self._isx.project_movie(files['videos'], mean_proj, stat_type='mean')
        self._isx.motion_correct(files['videos'], mc, max_translation=20, reference_file_name=mean_proj,
                                  output_translation_files=trans, output_crop_rect_file=crop)
        return { 'videos': mc, 'translations': trans, 'crop_rect': crop, 'mean_projection': mean_proj }
    
    def _normalize_dff_result(self, files, dff):
        self._isx.dff(files['videos'], dff, f0_type='mean')
        return { 'videos': dff }
    
    def _extract_neurons_pca_ica_result(self, files, ic):
        self._isx.pca_ica(files['videos'], ic, 180, int(1.15 * 180), block_size=1000)
        return { 'cellsets': ic }
    
    def _detect_events_in_cells_result(self, files, events):
        self._isx.event_detection(files['cellsets'], events, threshold=5)
        return { 'events': events }