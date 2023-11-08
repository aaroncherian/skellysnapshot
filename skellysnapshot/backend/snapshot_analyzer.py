from skellysnapshot.backend.calibration.anipose_object_loader import load_anipose_calibration_toml_from_path
from skellysnapshot.backend.constants import TaskNames
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread


class SnapshotAnalyzer:
    def __init__(self):
        self.snapshot2d_data = None
        self.snapshot3d_data = None

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

    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        # print(snapshot2d_data.data_2d_camera_frame_marker_dimension.shape)

        # print(self.snapshot3d_data.data_3d_camera_frame_marker_dimension.shape)
