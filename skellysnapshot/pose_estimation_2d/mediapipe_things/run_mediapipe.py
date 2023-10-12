from typing import Dict

import mediapipe as mp
import numpy as np

from skellysnapshot.pose_estimation_2d.mediapipe_things.mediapipe_config import mediapipe_parameters
from skellysnapshot.pose_estimation_2d.mediapipe_things.mediapipe_image_processing import process_image
from skellysnapshot.pose_estimation_2d.snapshot_data_2d import SnapshotData2d

mp_holistic = mp.solutions.holistic



def run_mediapipe_detection(snapshot: Dict[str, np.ndarray]):

    XY_data_for_all_cameras_list = []
    visibility_data_for_all_cameras_list = []
    annotated_images = {}

    holistic_tracker = mp_holistic.Holistic(
    model_complexity=mediapipe_parameters['model_complexity'],
    min_detection_confidence=mediapipe_parameters['min_detection_confidence'],
    min_tracking_confidence=mediapipe_parameters['min_tracking_confidence'],
    static_image_mode=mediapipe_parameters['static_image_mode'],
)

    for cam_key, image in snapshot.items():
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

    return SnapshotData2d(data_2d_camera_frame_marker_dimension=XY_data_for_all_cameras,
                          data_2d_camera_marker_visibility=visibility_data_for_all_cameras,
                          annotated_images=annotated_images)


if __name__ == '__main__':
    from pathlib import Path
    import cv2

    path_to_snapshot_images_folder = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_images')

    # Initialize an empty dictionary to hold the camera images
    snapshot = {}

    # Loop through each file in the directory to read the images into the dictionary
    for count, image_file in enumerate(path_to_snapshot_images_folder.iterdir()):
        if image_file.is_file() and image_file.suffix == '.jpg':  # or '.png' or whatever format you're using
            # Read the image using OpenCV (cv2.imread returns a NumPy array)
            image = cv2.imread(str(image_file))

            # Use the name of the file (without the extension) as the key, e.g., 'Cam_1'
            key = f'cam_{count}'

            # Add the image to the dictionary
            snapshot[key] = image

    snapshot_data_2d = run_mediapipe_detection(snapshot)
    
    for cam_key, annotated_img in snapshot_data_2d.annotated_images.items():
        cv2.imshow(f'Annotated Image from {cam_key}', annotated_img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    f = 2
