from typing import Dict

import mediapipe as mp
import numpy as np
from rich.progress import track
from skelly_tracker.trackers.mediapipe_tracker.mediapipe_holistic_tracker import (
    MediapipeHolisticTracker,
)

from skellysnapshot.backend.pose_estimation_2d.snapshot_data_2d_dataclass import (
    SnapshotData2d,
)


def run_mediapipe_detection(snapshot: Dict[str, np.ndarray]) -> SnapshotData2d:
    """Run the MediaPipe Holistic model on the input images and return the results in a SnapshotData2d object."""
    # This function can easily be generalized to take in a tracker as an argument, and will not be mediapipe dependent.
    XY_data_for_all_cameras_list = []
    annotated_images = {}

    tracker = MediapipeHolisticTracker(static_image_mode=True)

    for cam_key, image in snapshot.items():
        image_size = (image.shape[1], image.shape[0])
        tracker.process_image(image)
        tracker.recorder.record(tracker.tracked_objects)

        XY_data_for_all_cameras_list.append(
            tracker.recorder.process_tracked_objects(image_size=image_size)
        )
        annotated_images[cam_key] = tracker.annotated_image

        tracker.recorder.clear_recorded_objects()

    XY_data_for_all_cameras = np.stack(XY_data_for_all_cameras_list, axis=0)
    XY_data_for_all_cameras = XY_data_for_all_cameras[:,:,:,0:2]
    return SnapshotData2d(
        data_2d_camera_frame_marker_dimension=XY_data_for_all_cameras,
        annotated_images=annotated_images,
    )


if __name__ == "__main__":
    from pathlib import Path
    import cv2

    path_to_snapshot_images_folder = Path(
        r"C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_images"
    )

    # Initialize an empty dictionary to hold the camera images
    snapshot = {}

    # Loop through each file in the directory to read the images into the dictionary
    for count, image_file in enumerate(path_to_snapshot_images_folder.iterdir()):
        if (
            image_file.is_file() and image_file.suffix == ".jpg"
        ):  # or '.png' or whatever format you're using
            # Read the image using OpenCV (cv2.imread returns a NumPy array)
            image = cv2.imread(str(image_file))

            # Use the name of the file (without the extension) as the key, e.g., 'Cam_1'
            key = f"cam_{count}"

            # Add the image to the dictionary
            snapshot[key] = image

    snapshot_data_2d = run_mediapipe_detection(snapshot)

    for cam_key, annotated_img in snapshot_data_2d.annotated_images.items():
        cv2.imshow(f"Annotated Image from {cam_key}", annotated_img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    f = 2
