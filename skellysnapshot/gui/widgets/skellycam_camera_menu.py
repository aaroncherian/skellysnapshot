import sys

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from skellycam.frontend import SkellyCamWidget

import cv2

import logging

class SkellyCameraMenu(QWidget):
    snapshot_captured = Signal(object)

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        # Add capture button
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.capture_button = QPushButton("Capture Snapshot")
        self.capture_button.setEnabled(False)  # Disabled initially
        self.capture_button.clicked.connect(self.initiate_snapshot_process)
        self._layout.addWidget(self.capture_button)

        self._skellycam_widget = SkellyCamWidget(parent=self)
        self._layout.addWidget(self._skellycam_widget)

        self._skellycam_widget._manager._frame_grabber.new_frames.connect(self.handle_new_frames)
        self.countdown_timer = 0
        
        self.num_snapshots = 20  # Number of snapshots to capture
        self.snapshot_interval = 100  # Interval in milliseconds (100ms = 0.1s)
        self.snapshot_count = 0  # Counter for snapshots taken
        self.frame_number = 0 # Counter for snapshot IDS


        self.waiting_for_snapshot = False  # Flag to indicate waiting for a snapshot

    def handle_new_frames(self, multi_frame_payload):
        if self.waiting_for_snapshot:
            snapshot_payload = self.process_payload(multi_frame_payload, self.frame_number)
            if snapshot_payload:  # Only emit if payload processing was successful
                snapshot = {'id': self.frame_number, 'payload': snapshot_payload}
                self.snapshot_captured.emit(snapshot)
            self.waiting_for_snapshot = False
            logging.info(f"Snapshot {self.frame_number} emitted.")

    def process_payload(self, payload, frame_id):
        # Convert the received payload into the desired snapshot format
        snapshot = {}

        for cam_name, frame in payload.frames.items():

            try:
                snapshot[cam_name] = cv2.cvtColor(frame.get_image(), cv2.COLOR_BGR2RGB)
            except Exception as e:
                logging.error(f"Error processing frame from camera {cam_name} in frame {frame_id}: {e}")
                continue

        if not snapshot:
            logging.warning(f"No valid frames processed for frame {frame_id}.")
            return None

        return snapshot

    def initiate_snapshot_process(self):
        # Start with the countdown timer before taking the first snapshot
        QTimer.singleShot(self.countdown_timer * 1000, self.capture_first_snapshot)


    def capture_first_snapshot(self):
        # Capture the first snapshot and then start the repeated capture process
        self.snapshot_count = 0  # Reset counter
        self.frame_number = 0
        self.set_waiting_for_snapshot()
        QTimer.singleShot(self.snapshot_interval, self.repeated_capture)

    def repeated_capture(self):
        if self.snapshot_count < self.num_snapshots:
            self.frame_number += 1
            self.set_waiting_for_snapshot()
            QTimer.singleShot(self.snapshot_interval, self.repeated_capture)
            self.snapshot_count += 1
        else:
           logging.info(f'Snapshot capture complete. Captured {self.snapshot_count} snapshots.')


    def set_waiting_for_snapshot(self):
        # This method sets the flag to indicate the snapshot should be captured
        logging.info(f"Waiting for snapshot {self.frame_number}")
        self.waiting_for_snapshot = True

    def enable_capture_button(self):
        self.capture_button.setEnabled(True)
        # self.calibration_loaded.emit(filePath)  # Forward the signal if needed

    def disable_capture_button(self):
        self.capture_button.setEnabled(False)

    # def capture_snapshot(self):
    #     self.waiting_for_snapshot = True


    def close(self):
        self._skellycam_widget.close()
        super().close()

    def update_countdown_timer(self, new_timer_value):
        """
        Update the countdown timer with a new value.

        Args:
            new_timer_value (int): The new countdown timer value in seconds.
        """
        self.countdown_timer = new_timer_value



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = SkellyCameraMenu(parent=None)
    main_menu.show()
    main_menu.enable_capture_button()
    sys.exit(app.exec())


