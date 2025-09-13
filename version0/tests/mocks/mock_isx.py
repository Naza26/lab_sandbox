import os


class MockedISX:
    def preprocess(self, input_files, output_files, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock preprocess: {input_file} -> {output_files[i]}")

    def spatial_filter(self, input_files, output_files, low_cutoff=None, high_cutoff=None, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock spatial_filter: {input_file} -> {output_files[i]}")

    def make_output_file_paths(self, input_files, output_directory, suffix, ext='isxd'):
        output_paths = []
        for input_file in input_files:
            basename = os.path.splitext(os.path.basename(input_file))[0]
            while '.' in basename:
                basename = os.path.splitext(basename)[0]
            if suffix:
                output_filename = f"{basename}-{suffix}.{ext}"
            else:
                output_filename = f"{basename}.{ext}"
            output_path = os.path.join(output_directory, output_filename)
            output_paths.append(output_path)
        return output_paths

    def project_movie(self, input_files, output_file, stat_type='mean', **kwargs):
        print(f"Mock project_movie: {input_files} -> {output_file} (stat_type: {stat_type})")

    def motion_correct(self, input_files, output_files, max_translation=20, reference_file_name=None,
                      output_translation_files=None, output_crop_rect_file=None, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock motion_correct: {input_file} -> {output_files[i]}")
        if output_translation_files:
            for trans_file in output_translation_files:
                print(f"Mock translation file: {trans_file}")

    def dff(self, input_files, output_files, f0_type='mean', window_size=None, percentile=None, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock dff: {input_file} -> {output_files[i]} (f0_type: {f0_type})")

    def pca_ica(self, input_files, output_files, num_components=None, num_cells=None, block_size=1000, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock pca_ica: {input_file} -> {output_files[i]}")

    def event_detection(self, input_files, output_files, threshold=5, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock event_detection: {input_file} -> {output_files[i]} (threshold: {threshold})")

    def auto_accept_reject(self, input_files, output_files, filters=None, max_fpr=None, max_fnr=None, **kwargs):
        for i, input_file in enumerate(input_files):
            if i < len(output_files):
                print(f"Mock auto_accept_reject: {input_file} -> {output_files[i]}")
