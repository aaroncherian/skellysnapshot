from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class SnapshotData2d:
    data_2d_camera_frame_marker_dimension: np.ndarray
    data_2d_camera_marker_visibility: np.ndarray
    annotated_images: Dict[str, np.ndarray]
