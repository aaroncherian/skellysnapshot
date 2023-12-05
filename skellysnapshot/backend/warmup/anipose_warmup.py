import numpy as np
from skellysnapshot.backend.calibration import freemocap_anipose
from pathlib import Path
from skellysnapshot.backend.calibration.anipose_object_loader import load_anipose_calibration_toml_from_path
from skellysnapshot.backend.reconstruction_3d.reconstruct_3d import triangulate_3d_data

import logging

def warmup_anipose():
    logging.info('Initiating Anipose warmup with dummy data')
    dummy_2d_data = np.ones((2,1,1,2))

    path_to_dummy_toml = Path(__file__).parent/'dummy_calibration.toml'

    dummy_calibration_object = load_anipose_calibration_toml_from_path(path_to_dummy_toml)

    triangulate_3d_data(anipose_calibration_object=dummy_calibration_object, mediapipe_2d_data=dummy_2d_data)
    logging.info('Anipose initialized')

