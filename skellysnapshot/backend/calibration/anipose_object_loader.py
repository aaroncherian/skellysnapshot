from pathlib import Path
from typing import Union

from skellysnapshot.backend.calibration import freemocap_anipose


def load_anipose_calibration_toml_from_path(
        camera_calibration_data_toml_path: Union[str, Path],
):
    try:
        anipose_calibration_object = freemocap_anipose.CameraGroup.load(str(camera_calibration_data_toml_path))

        return anipose_calibration_object
    except Exception as e:
        print(f"Failed to load anipose calibration info from {str(camera_calibration_data_toml_path)}")
        raise e


if __name__ == '__main__':
    calibration_toml_path = Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_12_49_06_calibration_3\sesh_2023-05-17_12_49_06_calibration_3_camera_calibration.toml")
    
    anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)

    f = 2