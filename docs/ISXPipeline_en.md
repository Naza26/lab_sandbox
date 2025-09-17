# ISXPipeline Documentation (English)

Generated: 2025-09-13 10:38
## Introduction
ISXPipeline is a high-level pipeline built on top of the Inscopix Python API (package `isx`). It orchestrates common calcium imaging preprocessing and analysis steps (preprocessing, filtering, motion correction, dF/F normalization, PCA-ICA cell extraction, event detection, and exports).

## Usage
Example usage to run a simple pipeline:
```python
from version0.isx_pipeline.isx_pipeline import ISXPipeline
from version0.logger.file_logger import FileLogger

logger = FileLogger('/path/to/output')
p = ISXPipeline.new('/path/to/input_folder_with_isxd', logger)\
    .preprocess_videos()\
    .bandpass_filter_videos()\
    .motion_correction_videos()\
    .normalize_dff_videos()\
    .extract_neurons_pca_ica()\
    .detect_events_in_cells()\
    .auto_accept_reject_cells()\
    .export_movie_to_tiff()
# Final outputs available in logger directory
```

## Implemented functions
### preprocess_videos
Calls to isx functions:
- (No direct isx calls detected; this step likely manages files or uses higher-level utilities.)

### bandpass_filter_videos
Calls to isx functions:
- `spatial_filter(input_movie_files, output_movie_files, low_cutoff=0.005, high_cutoff=0.5, retain_mean=False, subtract_global_minimum=True)`
  - Parameters and defaults:
    - input_movie_files
    - output_movie_files
    - low_cutoff = 0.005
    - high_cutoff = 0.5
    - retain_mean = False
    - subtract_global_minimum = True
  - Summary: Apply spatial bandpass filtering to each frame of one or more movies.

### motion_correction_videos
Calls to isx functions:
- `make_output_file_paths(in_files, out_dir, suffix, ext='isxd')`
  - Parameters and defaults:
    - in_files
    - out_dir
    - suffix
    - ext = 'isxd'
  - Summary: Like :func:`isx.make_output_file_path`, but for many files.
- `motion_correct(input_movie_files, output_movie_files, max_translation=20, low_bandpass_cutoff=0.004, high_bandpass_cutoff=0.016, roi=None, reference_segment_index=0, reference_frame_index=0, reference_file_name='', global_registration_weight=1.0, output_translation_files=None, output_crop_rect_file=None, preserve_input_dimensions=False)`
  - Parameters and defaults:
    - input_movie_files
    - output_movie_files
    - max_translation = 20
    - low_bandpass_cutoff = 0.004
    - high_bandpass_cutoff = 0.016
    - roi = None
    - reference_segment_index = 0
    - reference_frame_index = 0
    - reference_file_name = ''
    - global_registration_weight = 1.0
    - output_translation_files = None
    - output_crop_rect_file = None
    - preserve_input_dimensions = False
  - Summary: Motion correct movies to a reference frame.
- `project_movie(input_movie_files, output_image_file, stat_type='mean')`
  - Parameters and defaults:
    - input_movie_files
    - output_image_file
    - stat_type = 'mean'
  - Summary: Project movies to a single statistic image.

### normalize_dff_videos
Calls to isx functions:
- `dff(input_movie_files, output_movie_files, f0_type='mean')`
  - Parameters and defaults:
    - input_movie_files
    - output_movie_files
    - f0_type = 'mean'
  - Summary: Compute DF/F movies, where each output pixel value represents a relative change

### extract_neurons_pca_ica
Calls to isx functions:
- `pca_ica(input_movie_files, output_cell_set_files, num_pcs, num_ics=120, unmix_type='spatial', ica_temporal_weight=0, max_iterations=100, convergence_threshold=1e-05, block_size=1000, auto_estimate_num_ics=False, average_cell_diameter=13)`
  - Parameters and defaults:
    - input_movie_files
    - output_cell_set_files
    - num_pcs
    - num_ics = 120
    - unmix_type = 'spatial'
    - ica_temporal_weight = 0
    - max_iterations = 100
    - convergence_threshold = 1e-05
    - block_size = 1000
    - auto_estimate_num_ics = False
    - average_cell_diameter = 13
  - Summary: Run PCA-ICA cell identification on movies.

### detect_events_in_cells
Calls to isx functions:
- `event_detection(input_cell_set_files, output_event_set_files, threshold=5, tau=0.2, event_time_ref='beginning', ignore_negative_transients=True, accepted_cells_only=False)`
  - Parameters and defaults:
    - input_cell_set_files
    - output_event_set_files
    - threshold = 5
    - tau = 0.2
    - event_time_ref = 'beginning'
    - ignore_negative_transients = True
    - accepted_cells_only = False
  - Summary: Perform event detection on cell sets.

### auto_accept_reject_cells
Calls to isx functions:
- `auto_accept_reject(input_cell_set_files, input_event_set_files, filters=None)`
  - Parameters and defaults:
    - input_cell_set_files
    - input_event_set_files
    - filters = None
  - Summary: Automatically classify cell statuses as accepted or rejected.

### export_movie_to_tiff
Calls to isx functions:
- `export_movie_to_tiff(input_movie_files, output_tiff_file, write_invalid_frames=False)`
  - Parameters and defaults:
    - input_movie_files
    - output_tiff_file
    - write_invalid_frames = False
  - Summary: Export movies to a TIFF file.
- `make_output_file_paths(in_files, out_dir, suffix, ext='isxd')`
  - Parameters and defaults:
    - in_files
    - out_dir
    - suffix
    - ext = 'isxd'
  - Summary: Like :func:`isx.make_output_file_path`, but for many files.

## Extensibility
You can add new steps to ISXPipeline by creating a new method that wraps `self.step(name, fn)` and uses the `isx` API to process inputs and produce outputs. Reuse the private helpers `_input_and_output_files`, `_process_input_output_pairs`, and `_step_folder_path` to follow existing conventions.
