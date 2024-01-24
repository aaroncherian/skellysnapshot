
from dataclasses import dataclass
from skellysnapshot.backend.calibration.freemocap_anipose import CameraGroup


@dataclass
class SnapshotAnalyzerInit:
    """This class is used to initialize the SnapshotAnalyzer class."""
    anipose_calibration_object: CameraGroup
    task_list:list
 



