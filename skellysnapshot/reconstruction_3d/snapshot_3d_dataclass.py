from dataclasses import dataclass

import numpy as np


@dataclass
class SnapshotData3d:
    body_hands_face_3d_data: np.ndarray
    reprojection_error_3d:np.ndarray
