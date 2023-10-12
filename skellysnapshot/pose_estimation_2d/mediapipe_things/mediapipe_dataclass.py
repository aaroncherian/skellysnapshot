from dataclasses import dataclass

import numpy as np


@dataclass
class MediapipeLandmarkData:
    pose_landmarks: np.ndarray
    face_landmarks: np.ndarray
    left_hand_landmarks: np.ndarray
    right_hand_landmarks: np.ndarray
    body_hands_face_landmarks: np.ndarray
    pose_visibility: np.ndarray


