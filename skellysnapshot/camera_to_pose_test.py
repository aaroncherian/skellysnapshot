import cv2

from skellysnapshot.cameras.camera_test import main
from skellysnapshot.constants import TaskNames
from skellysnapshot.task_worker_thread import TaskWorkerThread


class MyClass:
    def __init__(self):
        self.snapshot3d_data = None

    def handle_all_tasks_completed(self, task_results: dict):
        snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        # self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        # print(snapshot2d_data.data_2d_camera_frame_marker_dimension.shape)

        for name, image in snapshot2d_data.annotated_images.items():
            print(name)

        # print(self.snapshot3d_data.data_3d_camera_frame_marker_dimension.shape)

    def run(self, snapshot, calibration_toml_path):
        # Load the calibration object
        # anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)
        anipose_calibration_object = None
        task_worker_thread = TaskWorkerThread(
            snapshot=snapshot,
            anipose_calibration_object=anipose_calibration_object,
            task_queue=[TaskNames.TASK_RUN_MEDIAPIPE],
            task_running_callback=None,
            task_completed_callback=None,
            all_tasks_completed_callback=self.handle_all_tasks_completed
        )

        task_worker_thread.start()
        task_worker_thread.join()  # Wait for the thread to finish

        # plot_frame_of_3d_skeleton(snapshot_data_3d=self.snapshot3d_data)




def my_snapshot_callback(snapshot):
    print('starting callback')
    my_class = MyClass()
    my_class.run(snapshot, [])

if __name__ == "__main__":
    main(snapshot_callback=my_snapshot_callback)