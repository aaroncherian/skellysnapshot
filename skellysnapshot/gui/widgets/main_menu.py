from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Create a label for the welcome message
        welcome_label = QLabel("Welcome to SkellySnapshot!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QGroupBox to encapsulate general information
        group_box = QGroupBox("General Information")
        group_layout = QVBoxLayout()

        # Create a QGroupBox to encapsulate calibration status
        calibration_groupbox = QGroupBox("Calibration Status")
        calibration_group_layout = QVBoxLayout()

        # Create a label to display calibration status
        self.calibration_status_label = QLabel("Not Loaded")
        calibration_group_layout.addWidget(self.calibration_status_label)
        calibration_groupbox.setLayout(calibration_group_layout)

        # Add widgets and layouts to the main layout
        layout.addWidget(welcome_label)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        layout.addWidget(calibration_groupbox)
        self.setLayout(layout)

    def update_calibration_status(self, is_loaded):
        if is_loaded:
            self.calibration_status_label.setText("Loaded")
        else:
            self.calibration_status_label.setText("Not Loaded")
