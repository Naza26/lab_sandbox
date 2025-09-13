# Documentación de ISXPipeline (Español)

Generado: 2025-09-13 10:38
## Introducción
ISXPipeline es una canalización (pipeline) de alto nivel construida sobre la API de Python de Inscopix (`isx`). Orquesta pasos comunes de preprocesamiento y análisis de imagen de calcio: preprocesamiento, filtrado, corrección de movimiento, normalización dF/F, extracción de células por PCA-ICA, detección de eventos y exportaciones.

## Uso
Ejemplo de uso para ejecutar una canalización simple:
```python
from version0.isx_pipeline.isx_pipeline import ISXPipeline
from version0.logger.file_logger import FileLogger

logger = FileLogger('/ruta/a/salida')
p = ISXPipeline.new('/ruta/a/carpeta_entrada_con_isxd', logger)\
    .preprocess_videos()\
    .bandpass_filter_videos()\
    .motion_correction_videos()\
    .normalize_dff_videos()\
    .extract_neurons_pca_ica()\
    .detect_events_in_cells()\
    .auto_accept_reject_cells()\
    .export_movie_to_tiff()
# Los resultados finales están disponibles en el directorio del logger
```

## Funciones implementadas
### preprocess_videos
Llamadas a funciones de isx:
- (No se detectaron llamadas directas a isx; este paso probablemente gestiona archivos o usa utilidades de mayor nivel.)

### bandpass_filter_videos
Llamadas a funciones de isx:
- `spatial_filter(input_movie_files, output_movie_files, low_cutoff=0.005, high_cutoff=0.5, retain_mean=False, subtract_global_minimum=True)`
  - Parámetros y valores por defecto:
    - input_movie_files
    - output_movie_files
    - low_cutoff = 0.005
    - high_cutoff = 0.5
    - retain_mean = False
    - subtract_global_minimum = True
  - Resumen: Apply spatial bandpass filtering to each frame of one or more movies.

### motion_correction_videos
Llamadas a funciones de isx:
- `make_output_file_paths(in_files, out_dir, suffix, ext='isxd')`
  - Parámetros y valores por defecto:
    - in_files
    - out_dir
    - suffix
    - ext = 'isxd'
  - Resumen: Like :func:`isx.make_output_file_path`, but for many files.
- `motion_correct(input_movie_files, output_movie_files, max_translation=20, low_bandpass_cutoff=0.004, high_bandpass_cutoff=0.016, roi=None, reference_segment_index=0, reference_frame_index=0, reference_file_name='', global_registration_weight=1.0, output_translation_files=None, output_crop_rect_file=None, preserve_input_dimensions=False)`
  - Parámetros y valores por defecto:
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
  - Resumen: Motion correct movies to a reference frame.
- `project_movie(input_movie_files, output_image_file, stat_type='mean')`
  - Parámetros y valores por defecto:
    - input_movie_files
    - output_image_file
    - stat_type = 'mean'
  - Resumen: Project movies to a single statistic image.

### normalize_dff_videos
Llamadas a funciones de isx:
- `dff(input_movie_files, output_movie_files, f0_type='mean')`
  - Parámetros y valores por defecto:
    - input_movie_files
    - output_movie_files
    - f0_type = 'mean'
  - Resumen: Compute DF/F movies, where each output pixel value represents a relative change

### extract_neurons_pca_ica
Llamadas a funciones de isx:
- `pca_ica(input_movie_files, output_cell_set_files, num_pcs, num_ics=120, unmix_type='spatial', ica_temporal_weight=0, max_iterations=100, convergence_threshold=1e-05, block_size=1000, auto_estimate_num_ics=False, average_cell_diameter=13)`
  - Parámetros y valores por defecto:
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
  - Resumen: Run PCA-ICA cell identification on movies.

### detect_events_in_cells
Llamadas a funciones de isx:
- `event_detection(input_cell_set_files, output_event_set_files, threshold=5, tau=0.2, event_time_ref='beginning', ignore_negative_transients=True, accepted_cells_only=False)`
  - Parámetros y valores por defecto:
    - input_cell_set_files
    - output_event_set_files
    - threshold = 5
    - tau = 0.2
    - event_time_ref = 'beginning'
    - ignore_negative_transients = True
    - accepted_cells_only = False
  - Resumen: Perform event detection on cell sets.

### auto_accept_reject_cells
Llamadas a funciones de isx:
- `auto_accept_reject(input_cell_set_files, input_event_set_files, filters=None)`
  - Parámetros y valores por defecto:
    - input_cell_set_files
    - input_event_set_files
    - filters = None
  - Resumen: Automatically classify cell statuses as accepted or rejected.

### export_movie_to_tiff
Llamadas a funciones de isx:
- `export_movie_to_tiff(input_movie_files, output_tiff_file, write_invalid_frames=False)`
  - Parámetros y valores por defecto:
    - input_movie_files
    - output_tiff_file
    - write_invalid_frames = False
  - Resumen: Export movies to a TIFF file.
- `make_output_file_paths(in_files, out_dir, suffix, ext='isxd')`
  - Parámetros y valores por defecto:
    - in_files
    - out_dir
    - suffix
    - ext = 'isxd'
  - Resumen: Like :func:`isx.make_output_file_path`, but for many files.

## Extensibilidad
Puede agregar nuevos pasos a ISXPipeline creando un nuevo método que envuelva `self.step(name, fn)` y utilice la API `isx` para procesar entradas y producir salidas. Reutilice las ayudas privadas `_input_and_output_files`, `_process_input_output_pairs` y `_step_folder_path` para seguir las convenciones existentes.
