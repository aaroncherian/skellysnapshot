from enum import Enum

class TaskNames(Enum):
        TASK_GET_CALIBRATION_OBJECT = 'get_calibration_object'
        TASK_RUN_MEDIAPIPE = 'run_mediapipe'
        TASK_RUN_3D_RECONSTRUCTION = 'run_3d_reconstruction'
        TASK_VISUALIZE_3D = 'visualize_3d'
        TASK_CALCULATE_CENTER_OF_MASS = 'calculate_center_of_mass'


class Colors(Enum):
        NOT_READY_COLOR = '#fd8300'
        READY_COLOR = '#00AEDC'