from skellysnapshot.backend.center_of_mass.calculate_center_of_mass import run_center_of_mass_calculations
from skellysnapshot.backend.constants import TaskNames
from skellysnapshot.backend.pose_estimation_2d.run_mediapipe import run_mediapipe_detection
from skellysnapshot.backend.reconstruction_3d.reconstruct_3d import process_2d_data_to_3d
from skellysnapshot.gui.models.snapshot_analyzer_init import SnapshotAnalyzerInit
import logging

from copy import deepcopy

class TaskWorker:
    def __init__(self, initialization_parameters: SnapshotAnalyzerInit):
        self.anipose_calibration_object = initialization_parameters.anipose_calibration_object.deepcopy()
        self.task_list = initialization_parameters.task_list


        self.running = True

        self.available_tasks = {
            TaskNames.TASK_RUN_MEDIAPIPE: self.run_2d_pose_estimation,
            TaskNames.TASK_RUN_3D_RECONSTRUCTION: self.run_3d_reconstruction,
            TaskNames.TASK_CALCULATE_CENTER_OF_MASS: self.run_calculate_center_of_mass
        }

        self.tasks = {}  
        for task_name in self.task_list:
            if task_name not in self.available_tasks:
                raise ValueError(f"The task '{task_name}' was not found in the available tasks.")
            self.tasks[task_name] = {'function': self.available_tasks[task_name], 'result': None}

        self.task_completed_callback = None

        logging.info(f'THIS IS THE OBJECT AT INIT {self.anipose_calibration_object}')

    def process_snapshot(self, snapshot):
        snapshot_id = snapshot['id']
        self.snapshot_id= snapshot_id
        logging.info(f'THIS IS THE OBJECT AT START OF SNAPSHOT {snapshot_id} {self.anipose_calibration_object}')
        self.snapshot_payload = snapshot['payload']

        for task_info in self.tasks.values():
            task_info['result'] = None  # Clear any previous results

        for task_name, task_info in self.tasks.items():
            logging.info(f"Running task {task_name} for snapshot {snapshot_id}.")
            try:
                is_completed, result = task_info['function']()
                task_info['result'] = result
                if self.task_completed_callback:
                    self.task_completed_callback(task_name, result if is_completed else None)
            except ValueError as e:
                logging.warning(f"Task {task_name} failed: {e} for snapshot {snapshot_id}.")

        logging.info(f"All tasks completed for snapshot {snapshot_id}.")
        logging.info(f'THIS IS THE OBJECT AT END OF SNAPSHOT {snapshot_id} {self.anipose_calibration_object}')
        self.tasks['snapshot_id'] = snapshot_id
        return self.tasks

    def run_2d_pose_estimation(self):
        snapshot_data_2d = run_mediapipe_detection(self.snapshot_payload)
        return True, snapshot_data_2d

    def run_3d_reconstruction(self):
        snapshot_data_2d = self.tasks[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        if snapshot_data_2d is None:
            raise ValueError("2D snapshot data is missing.")
        logging.info(f'THIS IS THE OBJECT AT RUN {self.snapshot_id} {self.anipose_calibration_object}')
        snapshot_data_3d = process_2d_data_to_3d(snapshot_data_2d, self.anipose_calibration_object)
        return True, snapshot_data_3d

    def run_calculate_center_of_mass(self):
        snapshot_data_3d = self.tasks[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        if snapshot_data_3d is None:
            raise ValueError("3D snapshot data is missing.")
        snapshot_center_of_mass_3d = run_center_of_mass_calculations(snapshot_data_3d.data_3d_camera_frame_marker_dimension)
        return True, snapshot_center_of_mass_3d
