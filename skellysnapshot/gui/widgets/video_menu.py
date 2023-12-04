from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
)

from skellysnapshot.gui.helpers.video_file_finder import get_video_paths
from PySide6.QtCore import Signal

import logging
import cv2
class VideoMenu(QWidget):
    snapshot_ready_signal = Signal(object)
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        
        # Folder selection button
        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.folder_button)

        # Display area
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.layout.addWidget(self.display_area)

        # Process button
        self.process_button = QPushButton("Process Videos")
        self.process_button.clicked.connect(self.process_videos)
        self.layout.addWidget(self.process_button)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            logging.info(f"Selected folder: {folder_path}")
            self.video_paths = get_video_paths(folder_path)

            self.display_area.clear()
            self.display_area.append(f"Selected Folder: {folder_path}\n")
            self.display_video_paths(self.video_paths)

    def display_video_paths(self, video_paths):
        # Assuming get_video_paths is a function that returns a list of video paths in the folder
        for path in video_paths:
            self.display_area.append(path)

    def process_videos(self):
        if self.video_paths:
            self.process_synced_videos_to_snapshots(self.video_paths)


    def process_synced_videos_to_snapshots(self, video_paths):
        logging.info('Processing videos to snapshots')
        caps = [cv2.VideoCapture(path) for path in video_paths]
        frame_id = 0

        while all(cap.isOpened() for cap in caps):
            snapshot = {'id': frame_id, 'payload': {}}
            for i, cap in enumerate(caps):
                ret, frame = cap.read()
                if ret:
                    snapshot['payload'][f'camera_{i}'] = frame
                else:
                    for c in caps: c.release()
                    return

            logging.info(f"Snapshot {frame_id} emitted.")
            self.snapshot_ready_signal.emit(snapshot)
            frame_id += 1

        for cap in caps:
            cap.release()
