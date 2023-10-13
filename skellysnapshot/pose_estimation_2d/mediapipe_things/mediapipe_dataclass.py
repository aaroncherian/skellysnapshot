from dataclasses import dataclass

import numpy as np


@dataclass
class MediapipeLandmarkData:
    pose_2d_data: np.ndarray
    face_2d_data: np.ndarray
    left_hand_2d_data: np.ndarray
    right_hand_2d_data: np.ndarray
    body_hands_face_2d_data: np.ndarray
    pose_visibility: np.ndarray


