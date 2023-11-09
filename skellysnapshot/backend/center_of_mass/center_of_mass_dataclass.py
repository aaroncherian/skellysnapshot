from dataclasses import dataclass

import numpy as np


@dataclass
class CenterOfMassData:
    segment_center_of_mass_xyz: np.ndarray
    total_body_center_of_mass_xyz: np.ndarray
