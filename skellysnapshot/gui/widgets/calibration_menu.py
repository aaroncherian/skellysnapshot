from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy, QGroupBox

from skellysnapshot.calibration.freemocap_anipose import CameraGroup  # Import the type

from typing import Union
from pathlib import Path

class CalibrationManager:
    def __init__(self, event_bus, app_state):
        self.event_bus = event_bus
        self.anipose_calibration_object = None  # This will hold the actual calibration data
        self.app_state = app_state


    def load_calibration_from_file(self, filepath: Union[str, Path]):
        try:
            self.anipose_calibration_object = CameraGroup.load(str(filepath))  # Directly load the object here
            print(f"Calibration object {self.anipose_calibration_object} loaded from {filepath}")

            # Publish the event if the object is valid
            self.app_state.update_calibration_state(self.anipose_calibration_object)

        except Exception as e:
            print(f"Failed to load calibration object from {filepath}: {e}")
            self.anipose_calibration_object = None  # Reset the object to None if loading fails

    def publish_calibration_event(self):
        if isinstance(self.anipose_calibration_object, CameraGroup):  # Validate the object type
            self.event_bus.publish('calibration_object_created', self.anipose_calibration_object)
        else:
            print(f"Failed to publish event: Invalid calibration object type. Calibration object must be of type CameraGroup, but is of type {type(self.anipose_calibration_object)}")

class CalibrationMenu(QWidget):
    calibration_toml_path_loaded = pyqtSignal(str)  # Signal emitted when a calibration file is loaded
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.calibration_object_label = QLabel("Calibration Object: Not Loaded")
        self.calibration_object_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Set the size policy to Fixed
        layout.addWidget(self.calibration_object_label)


        toml_calibration_group = QGroupBox("Load Calibration File")
        toml_cal_layout = QVBoxLayout()
        self.calibration_file_label = QLabel("Calibration File: Not Loaded")
        self.calibration_file_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Set the size policy to Fixed
        toml_cal_layout.addWidget(self.calibration_file_label)
        toml_calibration_group.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.button = QPushButton("Load Calibration File")
        self.button.clicked.connect(self.load_calibration_file)
        toml_cal_layout.addWidget(self.button)
        toml_calibration_group.setLayout(toml_cal_layout)
        layout.addWidget(toml_calibration_group)

        self.setLayout(layout)

    def load_calibration_file(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Calibration File", "", "TOML Files (*.toml);;All Files (*)")
        if filePath:
            # Display only the filename in the label
            filename = filePath.split('/')[-1]
            self.calibration_file_label.setText(f"Calibration File: {filename}")
            
            # Set the tooltip to show the full file path
            self.calibration_file_label.setToolTip(filePath)
            
            self.calibration_toml_path_loaded.emit(filePath)

    def update_calibration_object_status(self, is_loaded):
        if is_loaded:
            self.calibration_object_label.setText("Calibration Object: Loaded")
        else:
            self.calibration_object_label.setText("Calibration Object: Not Loaded")



if __name__ == '__main__':

#testing anipose calibration loading 
    class DummyEventBus:
        def publish(self, event_name, event_data):
            print(f"Published event: {event_name}, Data: {event_data}")

    # Initialize a dummy event bus
    dummy_event_bus = DummyEventBus()

    # Initialize your CalibrationManager
    calibration_manager = CalibrationManager(dummy_event_bus)
    path_to_toml = r"C:\Users\aaron\FreeMocap_Data\recording_sessions\session_2023-10-20_13_56_27\recording_14_01_50_gmt-4_calibration\recording_14_01_50_gmt-4_calibration_camera_calibration.toml"

    # Test case 1: Valid object
    print("Test case 1: Valid object")
    calibration_manager.load_calibration_from_file(path_to_toml)
    # Output should indicate success and an event should be published

    # Test case 2: Manually set the object to None and test
    print("Test case 2: Object set to None")
    calibration_manager.anipose_calibration_object = None
    calibration_manager.publish_calibration_event()
    # Output should indicate failure and no event should be published

    # Test case 3: Manually set the object to an invalid type and test
    print("Test case 3: Object set to invalid type")
    calibration_manager.anipose_calibration_object = "This is not a CameraGroup"
    calibration_manager.publish_calibration_event()
    # Output should indicate failure and no event should be published

    # Note that this is a simplified example. In your actual code, you might want to use proper unit testing frameworks and methodologies.
