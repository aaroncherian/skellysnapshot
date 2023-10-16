import matplotlib.pyplot as plt
import numpy as np

from skellysnapshot.reconstruction_3d.snapshot_3d_dataclass import SnapshotData3d
from skellysnapshot.visualize_3d.mediapipe_bone_connections import build_mediapipe_skeleton


def plot_frame_of_3d_skeleton(ax,snapshot_data_3d:SnapshotData3d):
    skeleton_3d_data = snapshot_data_3d.data_3d_camera_frame_marker_dimension

    # Calculate mean coordinates for centering the plot
    mx_skel = np.nanmean(skeleton_3d_data[:, 0:33, 0])
    my_skel = np.nanmean(skeleton_3d_data[:, 0:33, 1])
    mz_skel = np.nanmean(skeleton_3d_data[:, 0:33, 2])
    skel_3d_range = 900  # Define the range for plot

    # Get the x, y, z coordinates for the first (and only) frame of our snapshot
    skel_x = skeleton_3d_data[0, :, 0]
    skel_y = skeleton_3d_data[0, :, 1]
    skel_z = skeleton_3d_data[0, :, 2]

    # Plot the points
    ax.scatter(skel_x, skel_y, skel_z)

    bone_connections = build_mediapipe_skeleton(skeleton_3d_data)

    # Plot the bones
    for connection in bone_connections.keys():
        line_start_point = bone_connections[connection][0]
        line_end_point = bone_connections[connection][1]
        bone_x, bone_y, bone_z = [line_start_point[0], line_end_point[0]], [line_start_point[1], line_end_point[1]], [line_start_point[2], line_end_point[2]]
        ax.plot(bone_x, bone_y, bone_z)

    # Set axis limits
    ax.set_xlim([mx_skel - skel_3d_range, mx_skel + skel_3d_range])
    ax.set_ylim([my_skel - skel_3d_range, my_skel + skel_3d_range])
    ax.set_zlim([mz_skel - skel_3d_range, mz_skel + skel_3d_range])

    # plt.show()