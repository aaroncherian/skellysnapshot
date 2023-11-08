from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy, QGroupBox, QSpacerItem

from skellysnapshot.calibration.freemocap_anipose import CameraGroup  # Import the type

from typing import Union
from pathlib import Path

from skellysnapshot.constants import Colors
class CalibrationManager:
    def __init__(self, app_state):
        self.anipose_calibration_object = None  # This will hold the actual calibration data
        self.app_state = app_state


    def load_calibration_from_file(self, filepath: Union[str, Path]):
        try:
            self.anipose_calibration_object = CameraGroup.load(str(filepath))  # Directly load the object here
            print(f"Calibration object {self.anipose_calibration_object} loaded from {filepath}")

        except Exception as e:
            print(f"Failed to load calibration object from {filepath} with error: {e}")
            self.anipose_calibration_object = None  # Reset the object to None if loading fails
        
        self.app_state.update_calibration_state(self.anipose_calibration_object)

class CalibrationMenu(QWidget):
    calibration_toml_path_loaded = pyqtSignal(str)  # Signal emitted when a calibration file is loaded
    return_to_main_page_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.add_calibration_title_label(layout)
        self.add_calibration_object_label(layout)
        self.add_calibration_toml_groupbox(layout)
        self.add_return_to_main_page_button(layout)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def add_calibration_title_label(self,layout):
        calibration_title_label = QLabel("Load in Your Calibration Here")
        calibration_title_label.setObjectName("HeaderText")
        calibration_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calibration_title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(calibration_title_label)

    def add_calibration_object_label(self, layout):
        calibration_status_groupbox = QGroupBox("Calibration Status")
        calibration_status_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        calibration_status_layout = QVBoxLayout()

        self.calibration_object_label = QLabel("Calibration Object: Not Loaded")
        self.calibration_object_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Set the size policy to Fixed
        calibration_status_layout.addWidget(self.calibration_object_label)
        
        calibration_status_groupbox.setLayout(calibration_status_layout)
        layout.addWidget(calibration_status_groupbox)


    def add_calibration_toml_groupbox(self, layout):
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

    def add_return_to_main_page_button(self,layout):
        self.button = QPushButton("Return to Main Page")
        self.button.clicked.connect(self.return_to_main_page_signal)
        layout.addWidget(self.button)

    def emit_return_to_main_page_signal(self):
        self.return_to_main_page_signal.emit()



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
            self.calibration_object_label.setStyleSheet(f"color: {Colors.READY_COLOR.value};")
        else:
            self.calibration_object_label.setText("Calibration Object: Not Loaded")
            self.calibration_object_label.setStyleSheet(f"color: {Colors.NOT_READY_COLOR.value};")



if __name__ == '__main__':
    pass