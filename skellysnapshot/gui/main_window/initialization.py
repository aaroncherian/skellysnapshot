import sys

import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QLabel

from skellysnapshot.gui.widgets.skeleton_3d_view_widget import Skeleton3dViewWidget


def initialize_gui():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Snapshot Viewer")
    # window.setGeometry(200, 200, 800, 600)

    tab_widget = QTabWidget()

    window.setCentralWidget(tab_widget)
    window.show()

    return app, window, tab_widget


def add_snapshot_tab(tab_widget, snapshot_images, snapshot_data_3d):
    # Create a new tab widget
    new_tab = QWidget()
    main_layout = QHBoxLayout()

    label_layout = QVBoxLayout()

    for name, image in snapshot_images.items():
        # Convert the image to be compatible with PyQt6
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # Create a QLabel to hold the image
        label = QLabel()
        label.setPixmap(pixmap)
        label_layout.addWidget(label)

    skeleton_view = Skeleton3dViewWidget('3d plot')
    skeleton_view.setMinimumSize(600, 600)
    skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
    main_layout.addLayout(label_layout)
    main_layout.addWidget(skeleton_view)

    main_layout.addLayout(label_layout)

    # Add the layout to the tab
    new_tab.setLayout(main_layout)
    new_tab.adjustSize()
    new_tab_index = tab_widget.addTab(new_tab, f"Snapshot {tab_widget.count() + 1}")
    tab_widget.setCurrentIndex(new_tab_index)
