from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy
from skellysnapshot.calibration.anipose_object_loader import load_anipose_calibration_toml_from_path

class CalibrationManager(QObject):
    calibration_object_created = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.calibration_object = None  # This will hold the actual calibration data

    def load_calibration_from_file(self, filepath):
        try:
            # Assume load_calibration is a function that reads a file
            # and returns a calibration object
            self.anipose_calibration_object = load_anipose_calibration_toml_from_path(filepath)
            print(f"Calibration object loaded successfully from {filepath}")
            self.calibration_object_created.emit(self.anipose_calibration_object)

        except Exception as e:
            print(f"Failed to load calibration object from {filepath}: {e}")



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
