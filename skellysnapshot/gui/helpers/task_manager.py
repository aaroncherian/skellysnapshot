from PySide6.QtCore import QObject, Signal

from skellysnapshot.backend.constants import TaskNames
from skellysnapshot.backend.task_worker_thread import TaskWorkerThread


class TaskManager(QObject):
    new_results_ready = Signal(object, object, object)

    def __init__(self, app_state, queue_manager):
        super().__init__()
        self.app_state = app_state
        self.queue_manager = queue_manager  # QueueManager instance
        self.anipose_calibration_object = None

    def set_anipose_calibration_object(self, calibration_state):
        self.anipose_calibration_object = calibration_state.calibration_object
        print(f'Calibration {self.anipose_calibration_object} loaded into task manager')

    def process_snapshot(self, snapshot):
        if self.anipose_calibration_object is None:
            print("Calibration object not loaded.")
            return

        # Create a task object with necessary details
        task = {
            'snapshot': snapshot,
            'anipose_calibration_object': self.anipose_calibration_object,
            'task_queue': [TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION, TaskNames.TASK_CALCULATE_CENTER_OF_MASS],
            'task_running_callback': None,  # Define these callbacks if needed
            'task_completed_callback': None,
            'all_tasks_completed_callback': self.handle_all_tasks_completed
        }

        # Add the task to the QueueManager's queue
        self.queue_manager.add_task(task)

    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        self.snapshot_center_of_mass_data = task_results[TaskNames.TASK_CALCULATE_CENTER_OF_MASS]['result']
        self.new_results_ready.emit(self.snapshot2d_data, self.snapshot3d_data, self.snapshot_center_of_mass_data)
