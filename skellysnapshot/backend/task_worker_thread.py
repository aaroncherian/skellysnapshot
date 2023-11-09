import threading
from typing import Dict

import numpy as np

from skellysnapshot.backend.center_of_mass.calculate_center_of_mass import run_center_of_mass_calculations
from skellysnapshot.backend.constants import TaskNames
from skellysnapshot.backend.pose_estimation_2d.mediapipe_things.run_mediapipe import run_mediapipe_detection
from skellysnapshot.backend.reconstruction_3d.reconstruct_3d import process_2d_data_to_3d


class TaskWorkerThread(threading.Thread):
    def __init__(self, snapshot: Dict[str, np.ndarray], anipose_calibration_object, task_queue: list,
                 task_running_callback=None, task_completed_callback=None, all_tasks_completed_callback=None):
        super().__init__()
        self.snapshot = snapshot
        self.anipose_calibration_object = anipose_calibration_object
        self.task_queue = task_queue
        self.task_running_callback = task_running_callback
        self.task_completed_callback = task_completed_callback
        self.all_tasks_finished_callback = all_tasks_completed_callback

        self.available_tasks = {
            TaskNames.TASK_RUN_MEDIAPIPE: self.run_2d_pose_estimation,
            TaskNames.TASK_RUN_3D_RECONSTRUCTION: self.run_3d_reconstruction,
            TaskNames.TASK_CALCULATE_CENTER_OF_MASS: self.run_calculate_center_of_mass
        }

        self.tasks = {task_name: {'function': self.available_tasks[task_name], 'result': None} for task_name in
                      task_queue}

        for task_name in task_queue:
            try:
                self.tasks[task_name] = {'function': self.available_tasks[task_name], 'result': None}
            except KeyError:
                raise ValueError(
                    f"The task '{task_name}' was not found in the available tasks {self.available_tasks.keys()}")

    def run(self):
        print(f'Starting TaskWorkerThread for {self.task_queue}')
        for task_info in self.tasks.values():  # clear any previous results
            task_info['result'] = None

        for task_name, task_info in self.tasks.items():
            print(f'Running task {task_name}')

            if self.task_running_callback is not None:
                self.task_running_callback(task_name)

            try:
                # Run the function for each task and return a bool of if it is completed, and a result object
                is_completed, result = task_info['function']()
                task_info['result'] = result

                # Depending on if callback functions have been passed, return the result of the function, or None
                # if the task was not completed
                if self.task_completed_callback:
                    self.task_completed_callback(task_name, result if is_completed else None)
            except ValueError as e:
                print(f"Task {task_name} failed: {e}")

        if self.all_tasks_finished_callback:
            self.all_tasks_finished_callback(self.tasks)

    def run_2d_pose_estimation(self):
        snapshot_data_2d = run_mediapipe_detection(self.snapshot)
        return True, snapshot_data_2d

    def run_3d_reconstruction(self):
        snapshot_data_2d = self.tasks[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        if snapshot_data_2d is None:
            raise ValueError("2D snapshot data is missing.")
        snapshot_data_3d = process_2d_data_to_3d(snapshot_data_2d=snapshot_data_2d,
                                                 anipose_calibration_object=self.anipose_calibration_object)
        return True, snapshot_data_3d

    def run_calculate_center_of_mass(self):
        snapshot_data_3d = self.tasks[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        if snapshot_data_3d is None:
            raise ValueError("3D snapshot data is missing.")
        snapshot_center_of_mass_3d = run_center_of_mass_calculations(
            processed_skel3d_frame_marker_xyz=snapshot_data_3d.data_3d_camera_frame_marker_dimension)
        return True, snapshot_center_of_mass_3d

    # def visualize_3d(self):
    #     snapshot_data_3d = self.tasks[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
    #     if snapshot_data_3d is None:
    #         raise ValueError("3D snapshot data is missing.")
    #     skelly_plot_figure = plot_frame_of_3d_skeleton(snapshot_data_3d = snapshot_data_3d, mediapipe_skeleton = None)

    #     return True, skelly_plot_figure
