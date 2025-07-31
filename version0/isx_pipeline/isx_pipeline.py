import os
from ..ci_pipe.pipeline import CIPipe
import json

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
                json.dump({
                    "steps": [],
                    "inputs": inputs,
                    "output": []
                }, f, indent=4)

        return output_folder, trace_path
    
    def info(self):
        with open(self._trace_file, "r") as f:
            return json.load(f)


    @classmethod
    def _scan_files(self , input_folder: str):
        import os
        # Check existence
        files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.isxd')]
        return files

        # "preprocess_videos",
        # "bandpass_filter_videos",
        # "motion_correction_videos",

    def preprocess_videos(self):
        input_files = self.next_step_input()

        pp_files = self._isx.make_output_file_paths(input_files, self._output_folder, 'PP')
        return self.step('Preprocess Videos', lambda files, pp: self.preprocess_result(files, pp), pp_files)

    def preprocess_result(self,files, pp):
        self._isx.preprocess(files, pp)
        return { 'videos': pp }

    # def bandpass_filter_videos(input_files, output_dir):
    #     bp_files = isx.make_output_file_paths(input_files, output_dir, 'BP')
    #     isx.spatial_filter(input_files, bp_files, low_cutoff=0.005, high_cutoff=0.5)
    #     return bp_files
    #
    #
    # def motion_correction_videos(input_files, output_dir, series_name):
    #     mean_proj_file = os.path.join(output_dir, f'{series_name}-mean_image.isxd')
    #     isx.project_movie(input_files, mean_proj_file, stat_type='mean')
    #     mc_files = isx.make_output_file_paths(input_files, output_dir, 'MC')
    #     translation_files = isx.make_output_file_paths(mc_files, output_dir, 'translations', 'csv')
    #     crop_rect_file = os.path.join(output_dir, f'{series_name}-crop_rect.csv')
    #     isx.motion_correct(
    #         input_files, mc_files, max_translation=20, reference_file_name=mean_proj_file,
    #         low_bandpass_cutoff=None, high_bandpass_cutoff=None,
    #         output_translation_files=translation_files, output_crop_rect_file=crop_rect_file)
    #     return mc_files
