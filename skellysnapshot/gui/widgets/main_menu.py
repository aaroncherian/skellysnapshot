from PyQt6.QtWidgets import QWidget,QVBoxLayout, QLabel
class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        placeholder_label = QLabel("Placeholder")
        layout.addWidget(placeholder_label)

        self.setLayout(layout)

