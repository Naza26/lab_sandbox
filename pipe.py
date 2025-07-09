import os
import sys
import textwrap
from glob import glob
from itertools import chain
from pathlib import Path
from datetime import datetime

import isx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

import algorithms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp_output")

ALGORITHMS = {
    "preprocess_min_image": lambda input_path: algorithms.preprocess_min_image([input_path], "temp_output")[0],
    "preprocess_videos": lambda input_path: algorithms.preprocess_videos([input_path], "temp_output")[0],
    "bandpass_filter_videos": lambda input_path: algorithms.bandpass_filter_videos([input_path], "temp_output")[0],
    "motion_correction_videos": lambda input_path: algorithms.motion_correction_videos([input_path], "temp_output", "serie")[0],
    "normalize_dff_videos": lambda input_path: algorithms.normalize_dff_videos([input_path], "temp_output")[0],
    "extract_neurons_pca_ica": lambda input_path: algorithms.extract_neurons_pca_ica([input_path], "temp_output")[0],
    "detect_events_in_cells": lambda input_path: algorithms.detect_events_in_cells([input_path], "temp_output")[0],
}



def log_step(log_path: str, step: str, input_file: str, output_file: str):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] STEP: {step}\n")
        f.write(f"    Input: {input_file}\n")
        f.write(f"    Output: {output_file}\n\n")


def process(video_path: str, algorithms: list, log_path: str) -> list:
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file does not exist: {video_path}")

    if not video_path.endswith('.isxd'):
        raise ValueError(f"Input file must have .isxd extension: {video_path}")

    results = []
    current_input = video_path

    for alg_name in algorithms:
        if alg_name not in ALGORITHMS:
            raise ValueError(f"Algorithm {alg_name} not found in pipeline")

        print(f"Applying algorithm: {alg_name} to {current_input}")
        output = ALGORITHMS[alg_name](current_input)
        log_step(log_path, alg_name, current_input, output)

        results.append(output)
        current_input = output

    return results


def set_output(processed_paths: list, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    for i, path in enumerate(processed_paths):
        filename = os.path.basename(path)
        dst = os.path.join(output_dir, filename)
        if os.path.abspath(path) != os.path.abspath(dst):
            os.replace(path, dst)
        print(f"Saved result {i} to {dst}")


def apply_algorithms(input_path: str, output_dir: str, algorithms: list):
    log_path = os.path.join(output_dir, "pipeline_log.txt")
    if os.path.exists(log_path):
        os.remove(log_path)

    results = process(input_path, algorithms, log_path)
    set_output(results, output_dir)


if __name__ == "__main__":
    input_file = "2021-10-21-11-57-27_video_trig_0-efocus_1000-PP.isxd"
    output_folder = "results"
    algos_to_run = [
        "preprocess_videos",
        "bandpass_filter_videos",
        "motion_correction_videos",
        "normalize_dff_videos",
        "extract_neurons_pca_ica",
        "detect_events_in_cells"
    ]
    os.makedirs("temp_output", exist_ok=True)
    apply_algorithms(input_file, output_folder, algos_to_run)