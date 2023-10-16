from skellysnapshot.calibration.anipose_object_loader import load_anipose_calibration_toml_from_path
from skellysnapshot.constants import TaskNames
from skellysnapshot.task_worker_thread import TaskWorkerThread
from skellysnapshot.visualize_3d.create_3d_figure import plot_frame_of_3d_skeleton

import matplotlib.pyplot as plt

from skellysnapshot.camera_to_pose_test import add_snapshot_tab, initialize_gui
import sys

class MyClass:
    def __init__(self):
        self.snapshot3d_data = None

    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        # print(snapshot2d_data.data_2d_camera_frame_marker_dimension.shape)

        # print(self.snapshot3d_data.data_3d_camera_frame_marker_dimension.shape)

    def run(self, snapshot, calibration_toml_path):
        # Load the calibration object
        anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)
        # anipose_calibration_object = None
        task_worker_thread = TaskWorkerThread(
            snapshot=snapshot,
            anipose_calibration_object=anipose_calibration_object,
            task_queue=[TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION],
            task_running_callback=None,
            task_completed_callback=None,
            all_tasks_completed_callback=self.handle_all_tasks_completed
        )

        task_worker_thread.start()
        task_worker_thread.join()  # Wait for the thread to finish

        # plot_frame_of_3d_skeleton(snapshot_data_3d=self.snapshot3d_data)





def main(snapshot, path_to_calibration_toml, tab_widget):
    my_class = MyClass()
    my_class.run(snapshot, path_to_calibration_toml)

        # Assume snapshot_data is available here, replace with actual data
    snapshot_data = my_class.snapshot2d_data.annotated_images
    snapshot_data_3d = my_class.snapshot3d_data
    add_snapshot_tab(tab_widget, snapshot_data, snapshot_data_3d)

if __name__ == '__main__':
    from pathlib import Path
    import cv2

    path_to_snapshot_images_folder = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_2')
    path_to_calibration_toml = Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_12_49_06_calibration_3\sesh_2023-05-17_12_49_06_calibration_3_camera_calibration.toml")


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

    
    app, window, tab_widget = initialize_gui()
    main(snapshot, path_to_calibration_toml, tab_widget)

    sys.exit(app.exec())


