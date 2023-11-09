from dataclasses import dataclass

import numpy as np


@dataclass
class SnapshotData3d:
    data_3d_camera_frame_marker_dimension: np.ndarray
    reprojection_error_3d: np.ndarray
