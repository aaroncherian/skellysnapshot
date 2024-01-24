from PySide6.QtCore import QObject, Signal

from skellysnapshot.backend.constants import TaskNames
from skellysnapshot.backend.task_worker_thread import TaskWorker
from skellysnapshot.gui.models.snapshot_analyzer_init import SnapshotAnalyzerInit
import logging

class TaskManager(QObject):
    new_results_ready = Signal(int, object, object, object)

    def __init__(self, app_state, queue_manager):
        super().__init__()
        self.app_state = app_state
        self.queue_manager = queue_manager
        self.anipose_calibration_object = None
        self.queue_manager.task_completed.connect(self.handle_all_tasks_completed)

    def set_anipose_calibration_object(self, calibration_state):
        self.anipose_calibration_object = calibration_state.calibration_object
        logging.info(f'Calibration {self.anipose_calibration_object} loaded into task manager')
        init_params = SnapshotAnalyzerInit(self.anipose_calibration_object, [TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION, TaskNames.TASK_CALCULATE_CENTER_OF_MASS])
        self.queue_manager.initialize_workers(init_params)

    def process_snapshot(self, snapshot):
        if self.anipose_calibration_object is None:
            logging.warning("Calibration object not loaded.")
            return
        
        logging.info(f'Received snapshot {snapshot["id"]} in task manager and sending to queue manager for processing')
        task = {
            'id': snapshot['id'],
            'payload': snapshot['payload']
        }
        self.queue_manager.add_task(task)

    def handle_all_tasks_completed(self, task_results):
        # Assuming task_results is a dict with required fields
        self.snapshot_id = task_results['id']
        self.snapshot2d_data = task_results['snapshot2d_data']
        self.snapshot3d_data = task_results['snapshot3d_data']
        self.snapshot_center_of_mass_data = task_results['snapshot_center_of_mass_data']
        self.new_results_ready.emit(self.snapshot_id, self.snapshot2d_data, self.snapshot3d_data, self.snapshot_center_of_mass_data)
        logging.info(f'Snapshot results ready for {self.snapshot_id}')