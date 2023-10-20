
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout

from skellysnapshot.gui.widgets.main_menu import MainMenu
from skellysnapshot.gui.widgets.camera_menu import CameraMenu
from skellysnapshot.gui.widgets.results_widget import ResultsViewWidget
from skellysnapshot.main import MyClass
from skellysnapshot.calibration.anipose_object_loader import load_anipose_calibration_toml_from_path
from skellysnapshot.task_worker_thread import TaskWorkerThread
from skellysnapshot.constants import TaskNames


class LayoutManager:
    def __init__(self):
        self.tab_widget = QTabWidget()

    def initialize_layout(self):
        self.main_menu = MainMenu()
        self.tab_widget.addTab(self.main_menu, "Main Menu")

        self.camera_tab = CameraMenu()
        self.tab_widget.addTab(self.camera_tab, "Cameras")

    def add_results_tab(self, snapshot_2d_data, snapshot_3d_data):
        results_tab = ResultsViewWidget(snapshot_2d_data, snapshot_3d_data)
        new_tab_index = self.tab_widget.addTab(results_tab, f"Snapshot {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(new_tab_index)

class TaskManager(QObject):
    new_results_ready = pyqtSignal(object,object)
    def __init__(self, anipose_calibration_object=None):
        super().__init__()
        self.anipose_calibration_object = anipose_calibration_object

    def set_anipose_calibration_object(self, anipose_calibration_object):
        self.anipose_calibration_object = anipose_calibration_object

    def process_snapshot(self, snapshot):
        if self.anipose_calibration_object is None:
            print("Calibration object not loaded.")
            return

        task_worker_thread = TaskWorkerThread(
            snapshot=snapshot,
            anipose_calibration_object=self.anipose_calibration_object,
            task_queue=[TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION],
            task_running_callback=None,
            task_completed_callback=None,
            all_tasks_completed_callback=self.handle_all_tasks_completed
        )
        task_worker_thread.start()

    
    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        self.new_results_ready.emit(self.snapshot2d_data,self.snapshot3d_data)


class SnapshotGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.layout_manager = LayoutManager()
        self.task_manager = TaskManager()

        layout = QVBoxLayout()
        self.layout_manager.initialize_layout()
        layout.addWidget(self.layout_manager.tab_widget)
        self.setLayout(layout)

        self.connect_signals_to_slots()
    
    def load_calibration_object(self, path_to_calibration_toml):
        self.anipose_calibration_object = load_anipose_calibration_toml_from_path(path_to_calibration_toml)
        self.task_manager.set_anipose_calibration_object(self.anipose_calibration_object)
        # task_worker_thread.join()  # Wait for the thread to finish
    
    def connect_signals_to_slots(self):
        self.layout_manager.camera_tab.snapshot_captured.connect(self.on_snapshot_captured_signal)
        self.task_manager.new_results_ready.connect(self.on_results_ready_signal)
        self.layout_manager.camera_tab.calibration_widget.calibration_loaded.connect(self.load_calibration_object)

    def on_snapshot_captured_signal(self, snapshot):
        self.task_manager.process_snapshot(snapshot)

    def on_results_ready_signal(self, snapshot2d_data, snapshot3d_data):
        self.layout_manager.add_results_tab(snapshot2d_data, snapshot3d_data)


        # self.add_results_tab(self.snapshot2d_data.annotated_images, self.snapshot3d_data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.snapshot_gui = SnapshotGUI()
        self.setCentralWidget(self.snapshot_gui)


# def runGUI():

#     app = QApplication([])

#     # Get screen size
#     screen = app.primaryScreen()
#     screen_size = screen.size() 

#     win = MainWindow()
#     win.show()

#     # Set window size relative to screen size
#     win.resize(screen_size.width() * 0.7, screen_size.height() * 0.7)

#     app.exec()

def run_analysis(snapshot, path_to_calibration_toml):
    my_class = MyClass()
    my_class.run(snapshot, path_to_calibration_toml)

        # Assume snapshot_data is available here, replace with actual data
    snapshot_images = my_class.snapshot2d_data.annotated_images
    snapshot_data_3d = my_class.snapshot3d_data

    return snapshot_images, snapshot_data_3d

def runGUI():

    with open('skellysnapshot\gui\stylesheet.css', 'r') as f:
        stylesheet = f.read()

    app = QApplication([])
    win = MainWindow()
    app.setStyle('Fusion')
    app.setStyleSheet(stylesheet)
    win.show()
    app.exec()


# def runGUI():
#     app = QApplication([])

#     # Get screen size
#     screen = app.primaryScreen()
#     screen_size = screen.size()

#     win = MainWindow()
#     win.show()

#     # Set window size relative to screen size
#     win.resize(screen_size.width() * 0.7, screen_size.height() * 0.7)
    
#     # Initialize SnapshotGUI and add it to MainWindow
#     snapshot_gui = SnapshotGUI()
#     win.setCentralWidget(snapshot_gui)
    

#     # Simulate adding multiple snapshots
#     from pathlib import Path
#     import cv2

#     path_to_snapshot_images_folder = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_2')
#     path_to_calibration_toml = Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_12_49_06_calibration_3\sesh_2023-05-17_12_49_06_calibration_3_camera_calibration.toml")


#     # # Initialize an empty dictionary to hold the camera images
#     # snapshot = {}

#     # # Loop through each file in the directory to read the images into the dictionary
#     # for count, image_file in enumerate(path_to_snapshot_images_folder.iterdir()):
#     #     if image_file.is_file() and image_file.suffix == '.jpg':  # or '.png' or whatever format you're using
#     #         # Read the image using OpenCV (cv2.imread returns a NumPy array)
#     #         image = cv2.imread(str(image_file))

#     #         # Use the name of the file (without the extension) as the key, e.g., 'Cam_1'
#     #         key = f'cam_{count}'

#     #         # Add the image to the dictionary
#     #         snapshot[key] = image
    
#     # snapshot_images, snapshot_data_3d = run_analysis(snapshot, path_to_calibration_toml)
#     # snapshot_gui.process_snapshot(snapshot, path_to_calibration_toml)
#     # snapshot_gui.add_results_tab(snapshot_images, snapshot_data_3d)
#     # snapshot_gui.add_results_tab(snapshot2["image_data"], snapshot2["3d_data"])



#     app.exec()




if __name__ == "__main__":
    runGUI()