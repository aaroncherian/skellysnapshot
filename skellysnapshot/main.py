from PySide6.QtWidgets import QApplication

from skellysnapshot.gui.main_window.main_window import SkellySnapshotMainWindow

if __name__ == "__main__":
    with open('./gui/stylesheet.css', 'r') as f:
        stylesheet = f.read()

    app = QApplication([])
    win = SkellySnapshotMainWindow()
    # app.setStyle('Fusion')
    app.setStyleSheet(stylesheet)
    win.show()
    app.exec()
