from dataclasses import dataclass
import numpy as np
from typing import Dict

@dataclass
class SnapshotData2d:
    data_2d_camera_frame_marker_dimension: np.ndarray
    data_2d_camera_marker_visibility: np.ndarray
    annotated_images: Dict[str, np.ndarray]
