from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QSizePolicy,QSpacerItem

class ClickableGroupBox(QGroupBox):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add Welcome Label
        self.add_welcome_label(main_layout)

        # Add General Information GroupBox
        self.add_general_info_groupbox(main_layout)

        # Add Calibration Status GroupBox
        self.add_calibration_status_groupbox(main_layout)

        # Add Spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        main_layout.addItem(spacer)

    def add_welcome_label(self, layout):
        welcome_label = QLabel("Welcome to SkellySnapshot!")
        welcome_label.setObjectName("WelcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(welcome_label)

    def add_general_info_groupbox(self, layout):
        group_box = QGroupBox("General Information")
        group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        group_layout = QVBoxLayout()
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

    def add_calibration_status_groupbox(self, layout):
        self.calibration_groupbox = ClickableGroupBox("Calibration Status")
        self.calibration_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.calibration_groupbox.setMinimumHeight(100)
        calibration_layout = QVBoxLayout()


        self.not_loaded_text = 'Not Loaded'
        self.not_loaded_additional_info = 'Click here to load calibration'

        self.calibration_status_label = QLabel(self.not_loaded_text)
        self.calibration_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calibration_status_label.setStyleSheet("color: orange;")
        self.calibration_additional_info_label = QLabel(self.not_loaded_additional_info)
        self.calibration_additional_info_label.setObjectName("CalibrationAdditionalInfoLabel")

        calibration_layout.addWidget(self.calibration_status_label)
        calibration_layout.addWidget(self.calibration_additional_info_label)
        self.calibration_groupbox.setLayout(calibration_layout)

        layout.addWidget(self.calibration_groupbox)

    def update_calibration_status(self, is_loaded):
        if is_loaded:
            self.calibration_status_label.setText("Loaded")
            self.calibration_status_label.setStyleSheet("color: #00AEDC;")

            self.calibration_additional_info_label.setText('Loaded from .toml file')  

        else:
            self.calibration_status_label.setText(self.not_loaded_text)
            self.calibration_status_label.setStyleSheet("color: #FD5400;")
            self.calibration_additional_info_label.setText(self.not_loaded_additional_info)  