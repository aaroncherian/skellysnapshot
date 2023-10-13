from typing import Dict
import numpy as np
import threading

from skellysnapshot.constants import TaskNames
from skellysnapshot.pose_estimation_2d.mediapipe_things.run_mediapipe import run_mediapipe_detection
from skellysnapshot.reconstruction_3d.reconstruct_3d import process_2d_data_to_3d


class TaskWorkerThread(threading.Thread):
    def __init__(self, snapshot: Dict[str, np.ndarray], anipose_calibration_object,task_queue: list, task_running_callback=None, task_completed_callback=None, all_tasks_completed_callback=None):
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
        }

        self.tasks = {task_name: {'function': self.available_tasks[task_name], 'result': None} for task_name in
                task_queue}
        
        for task_name in task_queue:
            try:
                self.tasks[task_name] = {'function': self.available_tasks[task_name], 'result': None}
            except KeyError:
                raise ValueError(f"The task '{task_name}' was not found in the available tasks {self.available_tasks.keys()}")

    def run(self):
        for task_info in self.tasks.values():  # clear any previous results
            task_info['result'] = None

        for task_name, task_info in self.tasks.items():
            if self.task_running_callback is not None:
                self.task_running_callback(task_name)
            try:
                if self.task_running_callback is not None:
                    self.task_running_callback(task_name)

                is_completed, result = task_info['function']()
                task_info['result'] = result

                if self.task_completed_callback:
                    self.task_completed_callback(task_name, result if is_completed else None)

            except ValueError as e:
                print(f"Task {task_name} failed: {e}")

            # run the function for each task and return a bool of if it is completed, and a result object
            is_completed, result = task_info['function']()
            task_info['result'] = result

            # depending on if callback functions have been passed, return the result of the function, or None
            # if the task was not completed
            if self.task_completed_callback:
                    self.task_completed_callback(task_name, result if is_completed else None)

        if self.all_tasks_finished_callback:
                self.all_tasks_finished_callback(self.tasks)

    def run_2d_pose_estimation(self):
        snapshot_data_2d = run_mediapipe_detection(self.snapshot)
        return True, snapshot_data_2d
    
    def run_3d_reconstruction(self):
        if self.tasks[TaskNames.TASK_RUN_MEDIAPIPE['result']] is None:
            raise ValueError("2D snapshot data is missing.")
        snapshot_data_3d = process_2d_data_to_3d(snapshot_data_2d=TaskNames.TASK_RUN_MEDIAPIPE['result'], anipose_calibration_object=self.anipose_calibration_object)
        return True, snapshot_data_3d
         
    


                                

