from PySide6.QtWidgets import QMainWindow

from skellysnapshot.gui.gui_main import SkellySnapshotMainWidget


class SkellySnapshotMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.snapshot_gui = SkellySnapshotMainWidget(parent=self)
        self.setCentralWidget(self.snapshot_gui)

    def closeEvent(self, event):
        self.snapshot_gui.close()
