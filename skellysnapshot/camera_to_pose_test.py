from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow, QLabel, QVBoxLayout, QWidget
import sys
import cv2

from skellysnapshot.cameras.camera_test import main
from skellysnapshot.constants import TaskNames
from skellysnapshot.task_worker_thread import TaskWorkerThread
from calibration.anipose_object_loader import load_anipose_calibration_toml_from_path

def initialize_gui():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Snapshot Viewer")
    window.setGeometry(200, 200, 800, 600)

    tab_widget = QTabWidget()

    window.setCentralWidget(tab_widget)
    window.show()

    return app, window, tab_widget

# Function to add a new tab with the snapshot images
def add_snapshot_tab(tab_widget, snapshot_images):
    # Create a new tab widget
    new_tab = QWidget()
    layout = QVBoxLayout()

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
        layout.addWidget(label)

    # Add the layout to the tab
    new_tab.setLayout(layout)
    new_tab_index = tab_widget.addTab(new_tab, f"Snapshot {tab_widget.count() + 1}")
    tab_widget.setCurrentIndex(new_tab_index)


class MyClass:
    def __init__(self):
        self.snapshot3d_data = None

    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        # self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        # print(snapshot2d_data.data_2d_camera_frame_marker_dimension.shape)

        # print(self.snapshot3d_data.data_3d_camera_frame_marker_dimension.shape)

    def run(self, snapshot, calibration_toml_path):
        # Load the calibration object
        anipose_calibration_object = load_anipose_calibration_toml_from_path(calibration_toml_path)
        # anipose_calibration_object = None
        task_worker_thread = TaskWorkerThread(
            snapshot=snapshot,
            anipose_calibration_object=anipose_calibration_object,
            task_queue=[TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION],
            task_running_callback=None,
            task_completed_callback=None,
            all_tasks_completed_callback=self.handle_all_tasks_completed
        )

        task_worker_thread.start()
        task_worker_thread.join()  # Wait for the thread to finish

        # plot_frame_of_3d_skeleton(snapshot_data_3d=self.snapshot3d_data)




def my_snapshot_callback(snapshot, path_to_calibration_toml, tab_widget):
    my_class = MyClass()
    my_class.run(snapshot, path_to_calibration_toml)

    # Assume snapshot_data is available here, replace with actual data
    snapshot_data = my_class.snapshot2d_data.annotated_images
    add_snapshot_tab(tab_widget, snapshot_data)

if __name__ == "__main__":
    from pathlib import Path

    settings_dict = {
        'timer':4
    }

    path_to_calibration_toml = Path(r"C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-10-16_11_53_42\recording_11_59_27_gmt-4_calibration\recording_11_59_27_gmt-4_calibration_camera_calibration.toml")

    app, window, tab_widget = initialize_gui()

    def snapshot_callback_wrapper(snapshot):
        my_snapshot_callback(snapshot,path_to_calibration_toml ,tab_widget)

    main(snapshot_callback=snapshot_callback_wrapper,settings_dict=settings_dict)

    sys.exit(app.exec())