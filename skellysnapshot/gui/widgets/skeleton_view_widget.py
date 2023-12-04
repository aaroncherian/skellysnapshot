

from skellysnapshot.backend.visualize_3d.mediapipe_bone_connections import build_mediapipe_skeleton


import numpy as np

from skellysnapshot.backend.reconstruction_3d.snapshot_3d_dataclass import SnapshotData3d

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt



import pyqtgraph.opengl as gl
from pyqtgraph.Vector import Vector

import numpy as np

class SkeletonViewWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        # Initialize 3D view
        self.view = gl.GLViewWidget()
        self.layout.addWidget(self.view)

        # Scatter plot item for joints
        self.scatter = gl.GLScatterPlotItem()
        self.view.addItem(self.scatter)

        # Lines for bones
        self.bones = []
        self.skel_3d_range = 900  # Define the range for plot


        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignCenter)


    def plot_frame_of_3d_skeleton(self, snapshot_data_3d:SnapshotData3d):
        # Extract 3D coordinates
        skeleton_3d_data = snapshot_data_3d.data_3d_camera_frame_marker_dimension

        mx = np.nanmean(skeleton_3d_data[:, 0:33, 0])
        my = np.nanmean(skeleton_3d_data[:, 0:33, 1])
        mz = np.nanmean(skeleton_3d_data[:, 0:33, 2])

        skel_x = skeleton_3d_data[0, :, 0]
        skel_y = skeleton_3d_data[0, :, 1]
        skel_z = skeleton_3d_data[0, :, 2]
        
        # Update scatter plot
        self.scatter.setData(pos=np.vstack([skel_x, skel_y, skel_z]).T)

        # Draw bones
        bone_connections = build_mediapipe_skeleton(skeleton_3d_data)
        for bone in self.bones:  # Remove existing bones
            self.view.removeItem(bone)
        self.bones = []
        for connection in bone_connections.keys():
            start, end = bone_connections[connection]
            line = gl.GLLinePlotItem(pos=np.array([start, end]), color=(1, 1, 1, 1), width=2)
            self.view.addItem(line)
            self.bones.append(line)

        # Set view limits
        self.set_view_limits(mx, my, mz)

    def plot_center_of_mass(self, snapshot_center_of_mass_data):
        # Extract center of mass data and plot
        com = snapshot_center_of_mass_data.total_body_center_of_mass_xyz[0]
        com_item = gl.GLScatterPlotItem(pos=np.array([com]), color=(1, 0, 1, 1), size=10)
        self.view.addItem(com_item)

    def update_3d_skeleton(self, new_snapshot_data_3d):
        # Recalculate mean coordinates for new data
        mx = np.nanmean(new_snapshot_data_3d[:, 0:33, 0])
        my = np.nanmean(new_snapshot_data_3d[:, 0:33, 1])
        mz = np.nanmean(new_snapshot_data_3d[:, 0:33, 2])

        # Update scatter plot for joints
        skel_x = new_snapshot_data_3d[0, :, 0]
        skel_y = new_snapshot_data_3d[0, :, 1]
        skel_z = new_snapshot_data_3d[0, :, 2]
        self.scatter.setData(pos=np.vstack([skel_x, skel_y, skel_z]).T)

        # Update bones
        bone_connections = build_mediapipe_skeleton(new_snapshot_data_3d)
        for bone in self.bones:
            self.view.removeItem(bone)
        self.bones = []
        for connection in bone_connections.keys():
            start, end = bone_connections[connection]
            line = gl.GLLinePlotItem(pos=np.array([start, end]), color=(1, 1, 1, 1), width=2)
            self.view.addItem(line)
            self.bones.append(line)

        # Update view limits
        self.update_view_limits(mx, my, mz)

    def update_center_of_mass(self, new_center_of_mass_data):
        com = new_center_of_mass_data
        if hasattr(self, 'com_item'):
            self.com_item.setData(pos=np.array([com]))
        else:
            self.com_item = gl.GLScatterPlotItem(pos=np.array([com]), color=(1, 0, 1, 1), size=10)
            self.view.addItem(self.com_item)

    def update_view_limits(self, mx, my, mz):
        self.view.opts['distance'] = max([self.skel_3d_range * 2])
        self.view.opts['center'] = Vector(mx, my, mz)
        self.view.opts['elevation'] = 30  # Adjust for initial view angle
        self.view.opts['azimuth'] = 45   # Adjust for initial view angle


    def update_title(self, new_title:str):
        self.title_label.setText(new_title)
        self.title_label.adjustSize()  # Adjust size to fit new text