import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from skellycam.frontend import SkellyCamWidget


class SkellyCameraMenu(QWidget):
    snapshot_captured = Signal(dict)
    calibration_loaded = Signal(str)  # Add this line if you want to forward the signal

    def __init__(self,
                 parent: QWidget, ):
        super().__init__(parent=parent)

        # Add capture button
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.capture_button = QPushButton("Capture Snapshot")
        self.capture_button.setEnabled(False)  # Disabled initially
        self.capture_button.clicked.connect(self.capture_snapshot)
        self._layout.addWidget(self.capture_button)

        self._skellycam_widget = SkellyCamWidget(parent=self)
        self._layout.addWidget(self._skellycam_widget)

    def enable_capture_button(self):
        self.capture_button.setEnabled(True)
        # self.calibration_loaded.emit(filePath)  # Forward the signal if needed

    def disable_capture_button(self):
        self.capture_button.setEnabled(False)

    def capture_snapshot(self):
        snapshot = {}
        for i, thread in enumerate(self.threads):
            frame = thread.capture_frame()
            if frame is not None:
                snapshot[f'cam_{i}'] = frame
        self.snapshot_captured.emit(snapshot)

    def close(self):
        self._skellycam_widget.close()
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = SkellyCameraMenu()
    main_menu.show()
    sys.exit(app.exec())
