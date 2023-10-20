from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Create a label for the welcome message
        welcome_label = QLabel("Welcome to SkellySnapshot!")
        welcome_label.setObjectName("WelcomeLabel")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # # Set the font properties
        # font = QFont()
        # font.setPointSize(24)
        # font.setBold(True)
        # welcome_label.setFont(font)

        # # Align the text to center
        # welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QGroupBox to encapsulate information
        group_box = QGroupBox("General Information")
        group_layout = QVBoxLayout()

        # Add widgets to the group layout
        layout.addWidget(welcome_label)

        # Add widgets and layouts
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)
