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
        self.num_snapshots = 0  # Number of snapshots to capture
        self.snapshot_interval = 100  # Interval in milliseconds (100ms = 0.1s)
        self.snapshot_count = 0  # Counter for snapshots taken
        self.frame_number = -1 # Counter for snapshot IDS (-1 because it gets incremented before the first snapshot is taken)


        self.waiting_for_snapshot = False  # Flag to indicate waiting for a snapshot


    def handle_new_frames(self, multi_frame_payload):
        if self.waiting_for_snapshot:
            unique_id = self.generate_unique_id()  # Generate a unique ID for the frame
            snapshot_payload = self.process_payload(multi_frame_payload, unique_id)
            logging.info(f"Snapshot {self.frame_number} emitted.")
            self.snapshot_captured.emit(snapshot_payload)
            self.waiting_for_snapshot = False

    def generate_unique_id(self):
        # Generate a unique ID. This could be a simple counter or a timestamp
        self.frame_number += 1
        return self.frame_number


    def process_payload(self, payload, frame_id):
        # Convert the received payload into the desired snapshot format
        snapshot = {'id': frame_id, 'payload': {}}


        for cam_name, frame in payload.frames.items():

            try:
                snapshot['payload'][cam_name] = cv2.cvtColor(frame.get_image(), cv2.COLOR_BGR2RGB)
            except Exception as e:
                logging.error(f"Error processing frame from camera {cam_name} in frame {frame_id}: {e}")
                continue

        if not snapshot:
            logging.warning(f"No valid frames processed for frame {frame_id}.")
            return None

        return snapshot

    def initiate_snapshot_process(self):
        # Start with the countdown timer before taking the first snapshot
        self.snapshot_count = 0  # Reset counter
        QTimer.singleShot(self.countdown_timer * 1000, self.capture_first_snapshot)


    def capture_first_snapshot(self):
        # Capture the first snapshot and then start the repeated capture process
        # self.frame_number = 0
        # self.set_waiting_for_snapshot()
        QTimer.singleShot(self.snapshot_interval, self.repeated_capture)

    def repeated_capture(self):
        # Check the condition at the beginning of the method
        self.snapshot_count += 1  # Increment first

        if self.snapshot_count > self.num_snapshots:
            logging.info(f'Snapshot capture complete. Captured {self.snapshot_count - 1} snapshots.')
            return  # Exit the method if the number of snapshots has been reached

        self.set_waiting_for_snapshot()

        # Schedule the next snapshot
        QTimer.singleShot(self.snapshot_interval, self.repeated_capture)


    def set_waiting_for_snapshot(self):
        # This method sets the flag to indicate the snapshot should be captured
        logging.info(f"Waiting for snapshot {self.frame_number+1}")
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

    def update_snapshot_settings(self, settings):
        """
        Update the camera menu with new snapshot settings.

        Args:
            settings (SnapshotSettings): The new snapshot settings.
        """
        self.countdown_timer = settings.countdown_timer
        self.num_snapshots = settings.num_snapshots
        self.snapshot_interval = settings.snapshot_interval



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = SkellyCameraMenu(parent=None)
    main_menu.show()
    main_menu.enable_capture_button()
    sys.exit(app.exec())


