import importlib
import json
import os
import shutil
from typing import ClassVar, Any
from rich.console import Console # type: ignore
from rich.table import Table # type: ignore
from rich.panel import Panel # type: ignore

import yaml

from ci_pipe.pipeline import CIPipe
from ci_pipe.trace_builder import TraceBuilder
from utils import build_filesystem_path_from, create_directory_from, list_directory_contents, last_part_of_path, \
    is_content_available_in


class ISXPipeline(CIPipe):
    INVALID_INPUT_DIRECTORY_ERROR = "Cannot create new pipeline with different input data in already created output directory"
    isx_package: ClassVar[Any] = importlib.import_module("isx")

    def __init__(self, inputs, logger, branch_name = "branch 1"):
        super().__init__(inputs)
        self.inputs = inputs
        self._isx = self.__class__.isx_package
        self._logger = logger
        self._output_folder = self._logger.directory()
        self._trace_file = self._logger.filepath()
        self._steps = []
        self.last_parameters = {}
        self.branch_name = branch_name
        self.defaults = self.read_config()
        self._completed_step_names = set()
        if not self._logger.is_empty():
            self._steps = TraceBuilder.build_steps_from_trace(
                self._logger.read_json_from_file(),
                branch_name=self.branch_name
            )
            self._completed_step_names = set(step.info()["name"] for step in self._steps)

    @classmethod
    def new(cls, input_directory, logger, branch_name = "branch 1"):
        if not is_content_available_in(input_directory) and is_content_available_in(logger.directory()):
            raise ValueError(cls.INVALID_INPUT_DIRECTORY_ERROR)
        inputs = cls._scan_files(input_directory)
        return cls(inputs, logger, branch_name)


    def branch(self, branch_name):
        new_pipeline = ISXPipeline(
            inputs=self.inputs,
            logger=self._logger,
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
    def _scan_files(cls, input_folder: str):
        files = [
            build_filesystem_path_from(input_folder, f) for f in list_directory_contents(input_folder) if
            f.endswith('.isxd')]
        return {"videos": files}

    def step(self, step_name, step_function, *args):
        if step_name in self._completed_step_names:
            return None
        step_folder_path = self._step_folder_path(step_name)
        create_directory_from(step_folder_path)

        result = super().step(step_name, step_function, *args)
        self._update_trace()
        self._completed_step_names.add(step_name)
        return result


    def trace(self):
        console = Console()
        try:
            with open(self._trace_file, "r") as f:
                full_trace = json.load(f)
            branch_trace = full_trace.get(self.branch_name)
            if branch_trace is None:
                console.print(f"[bold red]❌ Branch '{self.branch_name}' not found[/bold red]")
                return
        except Exception as e:
            console.print(f"[bold red]❌ Error loading trace: {e}[/bold red]")
            return

        steps_ordered = sorted(branch_trace.keys(), key=int)

        panels = []
        for step_number in steps_ordered:
            step_info = branch_trace[step_number]
            step_name = step_info.get("algorithm", f"Step {step_number}")
            panels.append(Panel(f"Step {step_number}\n{step_name}", padding=(1,2)))

        items = []
        for i, p in enumerate(panels):
            items.append(p)
            if i < len(panels) - 1:
                items.append("⬇")

        console.print(f"\n[bold underline]Pipeline Trace of branch: {self.branch_name}[/bold underline]\n")
        console.print(*items, justify="center")

    def info(self, step_number):
        console = Console()
        step_number = str(step_number)
        branch = self.branch_name 
        with open(self._trace_file) as f:
            trace = json.load(f)
        try:
            step = trace[branch][step_number]
        except KeyError:
            console.print(
                f"[bold red]❌ Step {step_number} not found in branch '{branch}'[/bold red]"
            )
            return
        table = Table(
            title=f"Step {step_number} Info",
            show_lines=True
        )
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="yellow")
        table.add_row("Algorithm", step.get("algorithm", ""))
        table.add_row("Input", "\n".join(step.get("input", [])))
        table.add_row("Output", "\n".join(step.get("output", [])))
        if "parameters" in step:
            params = "\n".join([f"{k}: {v}" for k, v in step["parameters"].items()])
            table.add_row("Parameters", params)
        console.print(table)


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
        step_entry = {
            "algorithm": step_info["name"],
            "input": [item for v in step_info["input"].values() for item in v],
            "output": [item for v in step_info["output"].values() for item in v],
        }

        if self.last_parameters:
            step_entry["parameters"] = self.last_parameters

        branch_trace[step_number] = step_entry


    def _input_and_output_files(self, input, input_key, step_name, output_suffix):
        input_files = input(input_key)
        step_folder = self._step_folder_path(step_name)
        input_output_pairs = []
        for in_file in input_files:
            out_file = self._isx.make_output_file_paths([in_file], step_folder, output_suffix)[0]
            input_output_pairs.append((in_file, out_file))
        return input_output_pairs
    
    def _create_output_folder(self, output_folder):
        os.makedirs(output_folder, exist_ok=True)

        trace_path = os.path.join(output_folder, "trace.json")
        if not os.path.exists(trace_path):
            with open(trace_path, 'w') as f:
                f.write("{}")
        return output_folder, trace_path


    @staticmethod
    def read_config(config_path=None):
        if config_path is None:
            # ruta absoluta del mismo directorio donde está este archivo
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "isx_config.yaml")
        if not os.path.exists(config_path):
            return {}  # si no existe, devolvemos dict vacío
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
        

    def get_parameters(self, name, **optional):
        cfg = self.defaults.get(name, {})
        parameters = dict(cfg)
        parameters.update(optional)
        self.last_parameters = parameters





# ----------- #
# Algoritmos  #
# ----------- #

    def preprocess_videos(self, name="Preprocess Videos"):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PP')
            self.last_parameters = {}
            self._process_input_output_pairs(input_output_pairs, self._isx.preprocess)
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))
    

    def bandpass_filter_videos(self, name="Bandpass Filter Videos", **kwargs):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'BP')
            self.get_parameters(name, **kwargs)
            self._process_input_output_pairs(
                 input_output_pairs,
                 lambda i, o: self._isx.spatial_filter(
                     i, o,
                     low_cutoff=self.last_parameters['low_cutoff'],
                     high_cutoff=self.last_parameters['high_cutoff']
                 )
             )
                 
            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))


    def motion_correction_videos(self, name="Motion Correction Videos", **kwargs):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'MC')
            self.get_parameters(name, **kwargs)
            step_folder = self._step_folder_path(name)
            mc_files = []
            translation_files = []
            mean_proj_files = []
            crop_rect_files = []
            series_name = self.last_parameters['series_name']
            max_translation = self.last_parameters['max_translation']
            for in_file, out_file in input_output_pairs:
                video_name = os.path.splitext(os.path.basename(in_file))[0]
                mean_proj_file = os.path.join(step_folder, f'{video_name}-{series_name}-mean_image.isxd')
                crop_rect_file = os.path.join(step_folder, f'{video_name}-{series_name}-crop_rect.csv')
                translation_file = self._isx.make_output_file_paths([out_file], step_folder, 'translations', 'csv')[0]

                self._isx.project_movie([in_file], mean_proj_file, stat_type='mean')
                self._isx.motion_correct([in_file], [out_file], max_translation=max_translation,
                                        reference_file_name=mean_proj_file,
                                        output_translation_files=[translation_file],
                                        output_crop_rect_file=crop_rect_file)

                mc_files.append(out_file)
                translation_files.append(translation_file)
                mean_proj_files.append(mean_proj_file)
                crop_rect_files.append(crop_rect_file)
            return {'videos': mc_files, 'translations': translation_files,
                    'crop_rect': crop_rect_files, 'mean_projection': mean_proj_files}

        return self.step(name, lambda input: wrapped_step(input))


    def normalize_dff_videos(self, name="Normalize dF/F Videos", **kwargs):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'DFF')
            self.get_parameters(name, **kwargs)


            self._process_input_output_pairs(input_output_pairs,
                lambda i, o: self._isx.dff(i, o, f0_type=self.last_parameters['f0_type']))

            return {'videos': [out_file for _, out_file in input_output_pairs]}

        return self.step(name, lambda input: wrapped_step(input))


    def extract_neurons_pca_ica(self, name="Extract Neurons PCA-ICA", **kwargs):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'videos', name, 'PCA-ICA')
            self.get_parameters(name, **kwargs)


            cellsets = []
            def pca_ica_fn(i, o):
                self._isx.pca_ica(i, o,
                                self.last_parameters['num_components'],
                                int(1.15 * self.last_parameters['num_components']),
                                block_size=self.last_parameters['block_size'])
                cellsets.append(o[0])
            
            self._process_input_output_pairs(input_output_pairs, pca_ica_fn)
            return {'cellsets': cellsets}

        return self.step(name, lambda input: wrapped_step(input))


    def detect_events_in_cells(self, name="Detect Events in Cells", **kwargs):
        def wrapped_step(input):
            input_output_pairs = self._input_and_output_files(input, 'cellsets', name, 'ED')
            self.get_parameters(name, **kwargs)


            events = []

            def event_fn(i, o):
                self._isx.event_detection(i, o, threshold=self.last_parameters['threshold'])
                events.append(o[0])

            self._process_input_output_pairs(input_output_pairs, event_fn)
            return {'events': events}

        return self.step(name, lambda input: wrapped_step(input))


    def auto_accept_reject_cells(self, name="Auto Accept-Reject Cells", **kwargs):
        def wrapped_step(input):
            input_cellsets = input('cellsets')
            copied_cellsets = self._copy_files_to_step_folder(input_cellsets, name)
            input_events = input('events')
            self.get_parameters(name, **kwargs)


            matches = self._match_events_to_cellsets(copied_cellsets, input_events)
            for cellset, event_file in matches.items():
                print(f"[auto_accept_reject] MATCH: {os.path.basename(cellset)} -> {os.path.basename(event_file)}")
                self._isx.auto_accept_reject([cellset], [event_file], self.last_parameters['filters'])

            return {'cellsets': copied_cellsets}

        return self.step(name, lambda input: wrapped_step(input))

# --------------------- #
# Usadas por algoritmos #
# --------------------- #

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
