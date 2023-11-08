
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout

from skellysnapshot.gui.widgets.main_menu import MainMenu
from skellysnapshot.gui.widgets.camera_menu import CameraMenu
from skellysnapshot.gui.widgets.results_widget import ResultsViewWidget
from skellysnapshot.gui.widgets.calibration_menu import CalibrationMenu, CalibrationManager
from skellysnapshot.main import MyClass

from skellysnapshot.task_worker_thread import TaskWorkerThread
from skellysnapshot.constants import TaskNames
from skellysnapshot.gui.app_state import AppState


import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s || %(levelname)s || %(funcName)s || %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class LayoutManager:
    def __init__(self):
        self.tab_widget = QTabWidget()
        self.tab_indices = {}
        self.results_tab = None


    def register_tab(self, tab, name):
        tab_index = self.tab_widget.addTab(tab, name)
        self.tab_indices[name] = tab_index
        

    # def initialize_layout(self):
    #     self.main_menu = MainMenu()
    #     self.tab_widget.addTab(self.main_menu, "Main Menu")

    #     self.camera_tab = CameraMenu()
    #     self.tab_widget.addTab(self.camera_tab, "Cameras")

    def add_results_tab(self, snapshot_2d_data, snapshot_3d_data, snapshot_center_of_mass_data):
        self.results_tab = ResultsViewWidget(snapshot_2d_data, snapshot_3d_data,snapshot_center_of_mass_data)
        new_tab_index = self.tab_widget.addTab(self.results_tab, f"Snapshot {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.results_tab.return_to_snapshot_tab_signal.connect(self.switch_to_camera_tab)


    def switch_to_calibration_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_indices['Calibration'])

    def switch_to_camera_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_indices['Cameras'])

class TaskManager(QObject):
    new_results_ready = pyqtSignal(object,object, object)
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state 
        self.anipose_calibration_object = None

    def set_anipose_calibration_object(self, calibration_state):
        self.anipose_calibration_object = calibration_state.calibration_object
        print(f'Calibration {self.anipose_calibration_object} loaded into task manager')

    def process_snapshot(self, snapshot):
        if self.anipose_calibration_object is None:
            print("Calibration object not loaded.")
            return

        task_worker_thread = TaskWorkerThread(
            snapshot=snapshot,
            anipose_calibration_object=self.anipose_calibration_object,
            task_queue=[TaskNames.TASK_RUN_MEDIAPIPE, TaskNames.TASK_RUN_3D_RECONSTRUCTION, TaskNames.TASK_CALCULATE_CENTER_OF_MASS],
            task_running_callback=None,
            task_completed_callback=None,
            all_tasks_completed_callback=self.handle_all_tasks_completed
        )
        task_worker_thread.start()

    
    def handle_all_tasks_completed(self, task_results: dict):
        self.snapshot2d_data = task_results[TaskNames.TASK_RUN_MEDIAPIPE]['result']
        self.snapshot3d_data = task_results[TaskNames.TASK_RUN_3D_RECONSTRUCTION]['result']
        self.snapshot_center_of_mass_data = task_results[TaskNames.TASK_CALCULATE_CENTER_OF_MASS]['result']
        self.new_results_ready.emit(self.snapshot2d_data,self.snapshot3d_data, self.snapshot_center_of_mass_data)



class SnapshotGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.app_state = AppState()

        self.main_menu = MainMenu()
        self.camera_menu = CameraMenu()
        self.calibration_menu = CalibrationMenu()

        self.layout_manager = LayoutManager()
        
        self.layout_manager.register_tab(self.main_menu, "Main Menu")
        self.layout_manager.register_tab(self.camera_menu, "Cameras")
        self.layout_manager.register_tab(self.calibration_menu, "Calibration")
        
        self.task_manager = TaskManager(self.app_state)
        self.calibration_manager = CalibrationManager(self.app_state)

        layout = QVBoxLayout()
        # self.layout_manager.initialize_layout()
        layout.addWidget(self.layout_manager.tab_widget)
        self.setLayout(layout)
        self.add_calibration_subscribers()
        self.add_enable_processing_subscribers()

        self.app_state.check_enable_conditions()
        self.app_state.check_initial_calibration_state()


        # self.connect_signals_to_event_bus()

        self.connect_signals_to_slots()
    
    def add_enable_processing_subscribers(self):
        enable_processing_subscribers = [
            self.check_enable_conditions,
            self.main_menu.update_process_snapshot_ready_status
        ]

        for subscriber in enable_processing_subscribers:
            self.app_state.subscribe("enable_processing", subscriber)

    def check_enable_conditions(self, all_conditions_met):
        if all_conditions_met:
            self.camera_menu.enable_capture_button()
        else:
            self.camera_menu.disable_capture_button()

    def add_calibration_subscribers(self):
        calibration_subscribers = [
            self.task_manager.set_anipose_calibration_object,
            # self.check_enable_conditions,
            lambda state: self.app_state.update_button_enable_conditions('calibration_loaded', state.status == "LOADED"),
            lambda state: self.main_menu.update_calibration_status(state.status == "LOADED"),
            lambda state: self.calibration_menu.update_calibration_object_status(state.status == "LOADED")
        ]
        
        for subscriber in calibration_subscribers:
            self.app_state.subscribe("calibration", subscriber)


    def connect_signals_to_slots(self):
        
        self.calibration_menu.calibration_toml_path_loaded.connect(self.calibration_manager.load_calibration_from_file)
        self.camera_menu.snapshot_captured.connect(self.on_snapshot_captured_signal)
        self.task_manager.new_results_ready.connect(self.on_results_ready_signal)
        self.main_menu.calibration_groupbox.clicked.connect(self.layout_manager.switch_to_calibration_tab)
        self.main_menu.process_snapshot_ready_group_box.clicked.connect(self.layout_manager.switch_to_camera_tab)

    def on_snapshot_captured_signal(self, snapshot):
        self.task_manager.process_snapshot(snapshot)

    def on_results_ready_signal(self, snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data):
        self.layout_manager.add_results_tab(snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data)


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
    # app.setStyle('Fusion')
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