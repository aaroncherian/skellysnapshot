from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication, QPushButton, QFileDialog
import cv2
import sys

class CalibrationWidget(QWidget):
    calibration_loaded = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label = QLabel("Calibration File: Not Loaded")
        layout.addWidget(self.label)

        self.button = QPushButton("Load Calibration File")
        self.button.clicked.connect(self.load_calibration_file)
        layout.addWidget(self.button)


        self.setLayout(layout)


    def load_calibration_file(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Calibration File", "", "TOML Files (*.toml);;All Files (*)")
        if filePath:
            self.label.setText(f"Calibration File: {filePath}")
            self.calibration_loaded.emit(filePath)

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage, int)

    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.latest_frame = None

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)
        while True:
            ret, frame = cap.read()
            if ret:
                self.latest_frame = frame  # Store the latest frame
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap_signal.emit(qt_image, self.camera_index)

    def capture_frame(self):
        return self.latest_frame

class CameraMenu(QWidget):
    snapshot_captured = pyqtSignal(dict)
    calibration_loaded = pyqtSignal(str)  # Add this line if you want to forward the signal

    def __init__(self, num_cameras=2):
        super().__init__()

        layout = QVBoxLayout()

        self.labels = {}
        self.threads = []  # To keep references
        for i in range(num_cameras):
            self.labels[i] = QLabel(f'Camera {i}')
            layout.addWidget(self.labels[i])
            thread = VideoThread(i)
            thread.change_pixmap_signal.connect(self.update_image)
            thread.start()
            self.threads.append(thread)  # Keep the reference

        # Add CalibrationWidget
        self.calibration_widget = CalibrationWidget()
        self.calibration_widget.calibration_loaded.connect(self.enable_capture_button)
        layout.addWidget(self.calibration_widget)

        # Add capture button
        self.capture_button = QPushButton("Capture Snapshot")
        self.capture_button.setEnabled(False)  # Disabled initially
        self.capture_button.clicked.connect(self.capture_snapshot)
        layout.addWidget(self.capture_button)

        self.setLayout(layout)

    def enable_capture_button(self, filePath):
        self.capture_button.setEnabled(True)
        self.calibration_loaded.emit(filePath)  # Forward the signal if needed

    def update_image(self, qt_image, camera_index):
        self.labels[camera_index].setPixmap(QPixmap.fromImage(qt_image))

    def capture_snapshot(self):
        snapshot = {}
        for i, thread in enumerate(self.threads):
            frame = thread.capture_frame()
            if frame is not None:
                snapshot[f'cam_{i}'] = frame
        self.snapshot_captured.emit(snapshot)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = CameraMenu()
    main_menu.show()
    sys.exit(app.exec())
