import numpy as np
import mediapipe as mp

from skellysnapshot.backend.pose_estimation_2d.mediapipe_things.mediapipe_dataclass import MediapipeLandmarkData

mp_holistic = mp.solutions.holistic


def initialize_empty_2d_arrays(num_points: int) -> np.ndarray:
    """Initializes an empty numpy array with shape (1, num_points, 2)."""
    return np.full((1, num_points, 2), np.nan)


def populate_arrays_with_landmarks(landmarks: np.ndarray, mediapipe_landmarks, image_width, image_height) -> np.ndarray:
    """Populates landmarks arrays with values."""
    for i, landmark in enumerate(mediapipe_landmarks.landmark):
        landmarks[0, i, :] = [landmark.x * image_width, landmark.y * image_height]
    return landmarks


def convert_mediapipe_results_to_numpy_arrays(mediapipe_results, image_width, image_height):
    # Initialize arrays with NaNs
    num_pose_points = len(mp_holistic.PoseLandmark)
    num_face_points = mp.solutions.face_mesh.FACEMESH_NUM_LANDMARKS_WITH_IRISES
    num_hand_points = len(mp_holistic.HandLandmark)

    pose_landmarks = initialize_empty_2d_arrays(num_pose_points)
    face_landmarks = initialize_empty_2d_arrays(num_face_points)
    left_hand_landmarks = initialize_empty_2d_arrays(num_hand_points)
    right_hand_landmarks = initialize_empty_2d_arrays(num_hand_points)

    pose_visibility = np.full((1, num_pose_points), np.nan)

    # Populate arrays with detected landmarks

    if mediapipe_results.pose_landmarks:
        pose_landmarks = populate_arrays_with_landmarks(pose_landmarks, mediapipe_results.pose_landmarks, image_width,
                                                        image_height)
        for i, landmark in enumerate(mediapipe_results.pose_landmarks.landmark):
            pose_visibility[0, i] = landmark.visibility
    if mediapipe_results.face_landmarks:
        face_landmarks = populate_arrays_with_landmarks(face_landmarks, mediapipe_results.face_landmarks, image_width,
                                                        image_height)
    if mediapipe_results.left_hand_landmarks:
        left_hand_landmarks = populate_arrays_with_landmarks(left_hand_landmarks, mediapipe_results.left_hand_landmarks,
                                                             image_width, image_height)
    if mediapipe_results.right_hand_landmarks:
        right_hand_landmarks = populate_arrays_with_landmarks(right_hand_landmarks,
                                                              mediapipe_results.right_hand_landmarks, image_width,
                                                              image_height)

    # Combine all landmarks into one array
    combined_landmarks = np.concatenate([pose_landmarks, right_hand_landmarks, left_hand_landmarks, face_landmarks],
                                        axis=1)

    return MediapipeLandmarkData(
        pose_2d_data=pose_landmarks,
        face_2d_data=face_landmarks,
        left_hand_2d_data=left_hand_landmarks,
        right_hand_2d_data=right_hand_landmarks,
        body_hands_face_2d_data=combined_landmarks,
        pose_visibility=pose_visibility
    )
