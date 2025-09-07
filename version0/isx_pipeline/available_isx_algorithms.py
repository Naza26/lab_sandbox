from enum import Enum


class AvailableISXAlgorithms(Enum):
    PREPROCESS_VIDEOS = "Preprocess Videos"
    BANDPASS_FILTER_VIDEOS = "Bandpass Filter Videos"
    MOTION_CORRECTION_VIDEOS = "Motion Correction Videos"
    NORMALIZE_DFF_VIDEOS = "Normalize dF/F Videos"
    EXTRACT_NEURONS_PCA_ICA = "Extract Neurons PCA-ICA"
    DETECT_EVENTS_IN_CELLS = "Detect Events in Cells"
    AUTO_ACCEPT_REJECT_CELLS = "Auto Accept-Reject Cells"
