import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from skellycam.frontend import SkellyCamWidget

import cv2
class SkellyCameraMenu(QWidget):
    snapshot_captured = Signal(object)

    def __init__(self, parent: QWidget):
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

        self._skellycam_widget._manager._frame_grabber.new_frames.connect(self.handle_new_frames)
        
        self.waiting_for_snapshot = False  # Flag to indicate waiting for a snapshot

    def handle_new_frames(self, multi_frame_payload):
        if self.waiting_for_snapshot:
            snapshot = self.process_payload(multi_frame_payload)
            self.snapshot_captured.emit(snapshot)
            self.waiting_for_snapshot = False

    def process_payload(self, payload):
        # Convert the received payload into the desired snapshot format
        snapshot = {}
        # Assuming payload is a dictionary or object you can iterate over
        for cam_name, frame in payload.frames.items():  # Adjust according to your payload's structure
            snapshot[cam_name] = cv2.cvtColor(frame.get_image(),cv2.COLOR_BGR2RGB)
        return snapshot

    def capture_snapshot(self):
        # When the button is pressed, set the flag to true
        # The next frame that comes in will be processed and emitted
        self.waiting_for_snapshot = True

    def enable_capture_button(self):
        self.capture_button.setEnabled(True)
        # self.calibration_loaded.emit(filePath)  # Forward the signal if needed

    def disable_capture_button(self):
        self.capture_button.setEnabled(False)

    def capture_snapshot(self):
        self.waiting_for_snapshot = True


    def close(self):
        self._skellycam_widget.close()
        super().close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = SkellyCameraMenu(parent=None)
    main_menu.show()
    main_menu.enable_capture_button()
    sys.exit(app.exec())


