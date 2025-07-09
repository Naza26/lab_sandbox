import os

import numpy as np
import isx


def preprocess_min_image(video_path: str) -> str:
    movie = isx.Movie.read(video_path)

    min_image = np.full(movie.spacing.num_pixels, np.iinfo(movie.data_type).max, dtype=movie.data_type)
    for i in range(movie.timing.num_samples):
        frame = movie.get_frame_data(i)
        min_image = np.minimum(min_image, frame)

    base_name = os.path.basename(video_path).replace('.isxd', '')
    output_path = f"{base_name}_min_image.isxd"
    isx.Image.write(output_path, movie.spacing, movie.data_type, min_image)
    return output_path

def preprocess_videos(input_files, output_dir):
    pp_files = isx.make_output_file_paths(input_files, output_dir, 'PP')
    isx.preprocess(input_files, pp_files, spatial_downsample_factor=2)
    return pp_files

def bandpass_filter_videos(input_files, output_dir):
    bp_files = isx.make_output_file_paths(input_files, output_dir, 'BP')
    isx.spatial_filter(input_files, bp_files, low_cutoff=0.005, high_cutoff=0.5)
    return bp_files

def motion_correction_videos(input_files, output_dir, series_name):
    mean_proj_file = os.path.join(output_dir, f'{series_name}-mean_image.isxd')
    isx.project_movie(input_files, mean_proj_file, stat_type='mean')
    mc_files = isx.make_output_file_paths(input_files, output_dir, 'MC')
    translation_files = isx.make_output_file_paths(mc_files, output_dir, 'translations', 'csv')
    crop_rect_file = os.path.join(output_dir, f'{series_name}-crop_rect.csv')
    isx.motion_correct(
        input_files, mc_files, max_translation=20, reference_file_name=mean_proj_file,
        low_bandpass_cutoff=None, high_bandpass_cutoff=None,
        output_translation_files=translation_files, output_crop_rect_file=crop_rect_file)
    return mc_files

def normalize_dff_videos(input_files, output_dir):
    dff_files = isx.make_output_file_paths(input_files, output_dir, 'DFF')
    isx.dff(input_files, dff_files, f0_type='mean')
    return dff_files

def extract_neurons_pca_ica(input_files, output_dir, num_cells=180):
    ic_files = isx.make_output_file_paths(input_files, output_dir, 'PCA-ICA')
    isx.pca_ica(input_files, ic_files, num_cells, int(1.15 * num_cells), block_size=1000)
    return ic_files

def detect_events_in_cells(cellset_files, output_dir, threshold=5):
    event_files = isx.make_output_file_paths(cellset_files, output_dir, 'ED')
    isx.event_detection(cellset_files, event_files, threshold=threshold)
    return event_files

def auto_accept_reject_cells(cellset_files, event_files):
    filters = [('SNR', '>', 3), ('Event Rate', '>', 0), ('# Comps', '=', 1)]
    isx.auto_accept_reject(cellset_files, event_files, filters=filters)

def longitudinal_registration(cellset_files, movie_files, output_dir):
    lr_cs_files = isx.make_output_file_paths(cellset_files, output_dir, 'LR')
    lr_movie_files = isx.make_output_file_paths(movie_files, output_dir, 'LR')
    lr_csv_file = os.path.join(output_dir, 'LR.csv')
    isx.longitudinal_registration(
        cellset_files, lr_cs_files, input_movie_files=movie_files,
        output_movie_files=lr_movie_files, csv_file=lr_csv_file, accepted_cells_only=True)
    return lr_cs_files, lr_movie_files

def export_results(movie_files, cellset_files, event_files, output_dir):
    tiff_movie_file = os.path.join(output_dir, 'DFF-LR.tif')
    isx.export_movie_to_tiff(movie_files, tiff_movie_file, write_invalid_frames=True)
    tiff_image_file = os.path.join(output_dir, 'DFF-PCA-ICA-LR.tif')
    csv_trace_file = os.path.join(output_dir, 'DFF-PCA-ICA-LR.csv')
    isx.export_cell_set_to_csv_tiff(cellset_files, csv_trace_file, tiff_image_file, time_ref='start')
    csv_event_file = os.path.join(output_dir, 'DFF-PCA-ICA-LR-ED.csv')
    isx.export_event_set_to_csv(event_files, csv_event_file, time_ref='start', sparse_output=False)
