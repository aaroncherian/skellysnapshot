from pathlib import Path
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic


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

@dataclass
class Data2D:
    data_2d_camera_frame_marker_dimension: np.ndarray
    data_2d_camera_marker_visibility: np.ndarray
    annotated_images: Dict[str, np.ndarray] 


mediapipe_parameters = {
    'model_complexity': 2,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'static_image_mode': True,
}


def initialize_empty_2d_arrays(num_points: int) -> np.ndarray:
    """Initializes an empty numpy array with shape (1, num_points, 2)."""
    return np.full((1, num_points, 2), np.nan)

def populate_arrays_with_landmarks(landmarks: np.ndarray, mediapipe_landmarks, image_width, image_height) -> np.ndarray:
    """Populates landmarks arrays with values."""
    for i, landmark in enumerate(mediapipe_landmarks.landmark):
        landmarks[0, i, :] = [landmark.x * image_width, landmark.y * image_height]
    return landmarks

def run_mediapipe_detection(snapshots: Dict[str, np.ndarray], holistic_tracker):
    XY_data_for_all_cameras_list = []
    visibility_data_for_all_cameras_list = []
    annotated_images = {}

    for cam_key, image in snapshots.items():
        # Process the image and get the landmark data and annotated image
        landmark_data, annotated_img = process_image(image, holistic_tracker)

        # Append the coordinates and visibility data to the lists
        XY_data_for_all_cameras_list.append(landmark_data.body_hands_face_landmarks)
        visibility_data_for_all_cameras_list.append(landmark_data.pose_visibility)

        # Add the annotated image to the dictionary
        annotated_images[cam_key] = annotated_img

    # Convert lists to NumPy arrays
    XY_data_for_all_cameras = np.stack(XY_data_for_all_cameras_list, axis=0)
    visibility_data_for_all_cameras = np.stack(visibility_data_for_all_cameras_list, axis=0)

    return Data2D(data_2d_camera_frame_marker_dimension=XY_data_for_all_cameras, 
                  data_2d_camera_marker_visibility=visibility_data_for_all_cameras, 
                  annotated_images = annotated_images)


def process_image(image, holistic_tracker):
    """Process a single image using the MediaPipe Holistic model.

    Args:
        image (np.array): The image to process.
        holistic_tracker (mp.solutions.Holistic): The MediaPipe Holistic model.

    Returns:
        results (mp.solutions.Holistic): The MediaPipe Holistic model results.
    """

    results = holistic_tracker.process(image)

    annotated_image = annotate_image(processed_image=image, mediapipe_results=results)

    image_height, image_width = image.shape[:2]
    mediapipe_landmark_dataclass  = convert_mediapipe_results_to_numpy_arrays(mediapipe_results=results, image_width=image_width, image_height=image_height)

    # # drawing the landmarks back on the image as a check     
    # for landmark in landmark_data.pose_landmarks[0]:
    #     x, y = int(landmark[0]), int(landmark[1])
    #     cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Draw green circle

    # cv2.imshow('Annotated Image', image)
    # cv2.waitKey(0)

    
    # f = 2

    return mediapipe_landmark_dataclass, annotated_image

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
        pose_landmarks = populate_arrays_with_landmarks(pose_landmarks, mediapipe_results.pose_landmarks, image_width, image_height)
        for i, landmark in enumerate(mediapipe_results.pose_landmarks.landmark):
            pose_visibility[0, i] = landmark.visibility
    if mediapipe_results.face_landmarks:
        face_landmarks = populate_arrays_with_landmarks(face_landmarks, mediapipe_results.face_landmarks, image_width, image_height)
    if mediapipe_results.left_hand_landmarks:
        left_hand_landmarks = populate_arrays_with_landmarks(left_hand_landmarks, mediapipe_results.left_hand_landmarks, image_width, image_height)
    if mediapipe_results.right_hand_landmarks:
        right_hand_landmarks = populate_arrays_with_landmarks(right_hand_landmarks, mediapipe_results.right_hand_landmarks, image_width, image_height)

    # Combine all landmarks into one array
    combined_landmarks = np.concatenate([pose_landmarks, right_hand_landmarks, left_hand_landmarks, face_landmarks], axis=1)

    return MediapipeLandmarkData(
        pose_landmarks=pose_landmarks,
        face_landmarks=face_landmarks,
        left_hand_landmarks=left_hand_landmarks,
        right_hand_landmarks=right_hand_landmarks,
        body_hands_face_landmarks=combined_landmarks,
        pose_visibility=pose_visibility
    )




def annotate_image(processed_image, mediapipe_results):
    
    # Draw the landmarks on the image
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    
    # Show the annotated image
    # cv2.imshow('Annotated Image', processed_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    annotated_image = processed_image
    return annotated_image    


holistic_tracker = mp_holistic.Holistic(
    model_complexity=mediapipe_parameters['model_complexity'],
    min_detection_confidence=mediapipe_parameters['min_detection_confidence'],
    min_tracking_confidence=mediapipe_parameters['min_tracking_confidence'],
    static_image_mode=mediapipe_parameters['static_image_mode'],
)

if __name__ == '__main__':

    path_to_snapshot_images_folder = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_images')

    # Initialize an empty dictionary to hold the camera images
    snapshots = {}

    # Loop through each file in the directory to read the images into the dictionary
    for count, image_file in enumerate(path_to_snapshot_images_folder.iterdir()):
        if image_file.is_file() and image_file.suffix == '.jpg':  # or '.png' or whatever format you're using
            # Read the image using OpenCV (cv2.imread returns a NumPy array)
            image = cv2.imread(str(image_file))
            
            # Use the name of the file (without the extension) as the key, e.g., 'Cam_1'
            key = f'cam_{count}'
            
            # Add the image to the dictionary
            snapshots[key] = image

    snapshot_data_2d = run_mediapipe_detection(snapshots, holistic_tracker)

    f = 2
