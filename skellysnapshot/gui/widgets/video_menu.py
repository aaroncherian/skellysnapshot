from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
)

from skellysnapshot.gui.helpers.video_file_finder import get_video_paths
from PySide6.QtCore import Signal

import logging
import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
)
from PySide6.QtCore import Signal, QObject, QThread
import cv2
import os

class VideoProcessingWorker(QObject):
    snapshot_ready = Signal(dict)
    finished = Signal()

    def __init__(self, video_paths):
        super().__init__()
        self.video_paths = video_paths

    def process_synced_videos_to_snapshots(self):
        caps = [cv2.VideoCapture(path) for path in self.video_paths]
        frame_id = 0

        while all(cap.isOpened() for cap in caps):
            snapshot = {'id': frame_id, 'payload': {}}
            for i, cap in enumerate(caps):
                ret, frame = cap.read()
                if ret:
                    snapshot['payload'][f'camera_{i}'] = frame
                else:
                    for c in caps: c.release()
                    self.finished.emit()
                    return

            self.snapshot_ready.emit(snapshot)
            frame_id += 1

        for cap in caps:
            cap.release()
        self.finished.emit()

class VideoMenu(QWidget):
    snapshot_ready_signal = Signal(dict)
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.folder_button)

        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.layout.addWidget(self.display_area)

        self.process_button = QPushButton("Process Videos")
        self.process_button.clicked.connect(self.process_videos)
        self.layout.addWidget(self.process_button)

        self.thread = None
        self.worker = None

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.video_paths = get_video_paths(folder_path)
            self.display_area.clear()
            self.display_area.append(f"Selected Folder: {folder_path}\n")
            self.display_video_paths(self.video_paths)

    def display_video_paths(self, video_paths):
        for path in video_paths:
            self.display_area.append(path)

    def process_videos(self):
        if self.video_paths:
            logging.info(f'Processing videos: {self.video_paths}')
            self.thread = QThread()
            self.worker = VideoProcessingWorker(self.video_paths)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.process_synced_videos_to_snapshots)
            self.worker.snapshot_ready.connect(self.handle_snapshot)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

    def handle_snapshot(self, snapshot):
        logging.info(f'Emitting snapshot {snapshot["id"]}')
        self.snapshot_ready_signal.emit(snapshot)
        
