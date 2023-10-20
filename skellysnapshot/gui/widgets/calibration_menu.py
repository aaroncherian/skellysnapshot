from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy

from skellysnapshot.calibration.freemocap_anipose import CameraGroup  # Import the type

from typing import Union
from pathlib import Path

class CalibrationManager:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.anipose_calibration_object = None  # This will hold the actual calibration data

    def load_calibration_from_file(self, filepath: Union[str, Path]):
        try:
            self.anipose_calibration_object = CameraGroup.load(str(filepath))  # Directly load the object here
            print(f"Calibration object {self.anipose_calibration_object} loaded from {filepath}")

            # Publish the event if the object is valid
            self.publish_calibration_event()

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

        self.label = QLabel("Calibration File: Not Loaded")
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Set the size policy to Fixed
        layout.addWidget(self.label)

        self.button = QPushButton("Load Calibration File")
        self.button.clicked.connect(self.load_calibration_file)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def load_calibration_file(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Calibration File", "", "TOML Files (*.toml);;All Files (*)")
        if filePath:
            # Display only the filename in the label
            filename = filePath.split('/')[-1]
            self.label.setText(f"Calibration File: {filename}")
            
            # Set the tooltip to show the full file path
            self.label.setToolTip(filePath)
            
            self.calibration_toml_path_loaded.emit(filePath)


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
