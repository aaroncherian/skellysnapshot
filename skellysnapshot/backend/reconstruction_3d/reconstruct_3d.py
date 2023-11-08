import numpy as np

from skellysnapshot.backend.pose_estimation_2d.snapshot_data_2d_dataclass import SnapshotData2d
from skellysnapshot.backend.reconstruction_3d.snapshot_3d_dataclass import SnapshotData3d


def process_2d_data_to_3d(snapshot_data_2d: SnapshotData2d, anipose_calibration_object):
    # Load calibration object
    body_hands_face_2d_data = snapshot_data_2d.data_2d_camera_frame_marker_dimension
    # 3D reconstruction
    snapshot_data_3d = triangulate_3d_data(
        anipose_calibration_object=anipose_calibration_object,
        mediapipe_2d_data=body_hands_face_2d_data,
    )

    return snapshot_data_3d


def triangulate_3d_data(
        anipose_calibration_object,
        mediapipe_2d_data: np.ndarray,
):
    # Validation
    number_of_cameras, number_of_frames, number_of_tracked_points, number_of_spatial_dimensions = mediapipe_2d_data.shape

    # Reshape data to collapse across 'frames' so it becomes [number_of_cameras, number_of_2d_points(numFrames*numPoints), XY]
    data2d_flat = mediapipe_2d_data.reshape(number_of_cameras, -1, 2)

    # Triangulate
    data3d_flat = anipose_calibration_object.triangulate(data2d_flat, progress=True)

    # Reshape the flat data back to [numFrames, numPoints, XYZ]
    spatial_data3d_numFrames_numTrackedPoints_XYZ = data3d_flat.reshape(number_of_frames, number_of_tracked_points, 3)

    # Compute reprojection error
    data3d_reprojectionError_flat = anipose_calibration_object.reprojection_error(data3d_flat, data2d_flat, mean=True)
    reprojection_error_data3d_numFrames_numTrackedPoints = data3d_reprojectionError_flat.reshape(number_of_frames,
                                                                                                 number_of_tracked_points)

    # Filter data with high reprojection error
    return SnapshotData3d(
        data_3d_camera_frame_marker_dimension=spatial_data3d_numFrames_numTrackedPoints_XYZ,
        reprojection_error_3d=reprojection_error_data3d_numFrames_numTrackedPoints, 
    )

# def threshold_by_confidence(
#     mediapipe_2d_data: np.ndarray,
#     mediapipe_confidence_cutoff_threshold: float = 0.0,
# ):
#     mediapipe_2d_data[mediapipe_2d_data <= mediapipe_confidence_cutoff_threshold] = np.NaN

#     number_of_nans = np.sum(np.isnan(mediapipe_2d_data))
#     number_of_points = np.prod(mediapipe_2d_data.shape)
#     percentage_that_are_nans = (np.sum(np.isnan(mediapipe_2d_data)) / number_of_points) * 100

#     return mediapipe_2d_data
