
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QVBoxLayout
from skellysnapshot.gui.widgets.main_menu import MainMenu
from skellysnapshot.gui.widgets.results_widget import ResultsViewWidget
from skellysnapshot.main import MyClass

class SnapshotGUI(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
    
        self.setWindowTitle("Snapshot GUI")
        self.tab_widget = QTabWidget()
        self.main_menu_tab = MainMenu()
        self.tab_widget.addTab(self.main_menu_tab, "Main Menu")

        layout.addWidget(self.tab_widget) 
        self.resize(1256, 1029)

        self.setLayout(layout)

    def add_results_tab(self, snapshot_images, snapshot_3d_data):
        
        results_tab = ResultsViewWidget(snapshot_images, snapshot_3d_data)
        new_tab_index = self.tab_widget.addTab(results_tab, f"Snapshot {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(new_tab_index)

        


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        widget = QWidget()
        postprocessing_window = SnapshotGUI()
        

        layout.addWidget(postprocessing_window)

        widget.setLayout(layout)
        self.setCentralWidget(widget)


# def runGUI():

#     app = QApplication([])

#     # Get screen size
#     screen = app.primaryScreen()
#     screen_size = screen.size() 

#     win = MainWindow()
#     win.show()

#     # Set window size relative to screen size
#     win.resize(screen_size.width() * 0.7, screen_size.height() * 0.7)

#     app.exec()

def run_analysis(snapshot, path_to_calibration_toml):
    my_class = MyClass()
    my_class.run(snapshot, path_to_calibration_toml)

        # Assume snapshot_data is available here, replace with actual data
    snapshot_images = my_class.snapshot2d_data.annotated_images
    snapshot_data_3d = my_class.snapshot3d_data

    return snapshot_images, snapshot_data_3d

def runGUI():
    app = QApplication([])

    # Get screen size
    screen = app.primaryScreen()
    screen_size = screen.size()

    win = MainWindow()
    win.show()

    # Set window size relative to screen size
    win.resize(screen_size.width() * 0.7, screen_size.height() * 0.7)
    
    # Initialize SnapshotGUI and add it to MainWindow
    snapshot_gui = SnapshotGUI()
    win.setCentralWidget(snapshot_gui)
    

    # Simulate adding multiple snapshots
    from pathlib import Path
    import cv2

    path_to_snapshot_images_folder = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test_2')
    path_to_calibration_toml = Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_12_49_06_calibration_3\sesh_2023-05-17_12_49_06_calibration_3_camera_calibration.toml")


    # Initialize an empty dictionary to hold the camera images
    snapshot = {}

    # Loop through each file in the directory to read the images into the dictionary
    for count, image_file in enumerate(path_to_snapshot_images_folder.iterdir()):
        if image_file.is_file() and image_file.suffix == '.jpg':  # or '.png' or whatever format you're using
            # Read the image using OpenCV (cv2.imread returns a NumPy array)
            image = cv2.imread(str(image_file))

            # Use the name of the file (without the extension) as the key, e.g., 'Cam_1'
            key = f'cam_{count}'

            # Add the image to the dictionary
            snapshot[key] = image
    
    snapshot_images, snapshot_data_3d = run_analysis(snapshot, path_to_calibration_toml)
    snapshot_gui.add_results_tab(snapshot_images, snapshot_data_3d)
    # snapshot_gui.add_results_tab(snapshot2["image_data"], snapshot2["3d_data"])



    app.exec()





if __name__ == "__main__":
    runGUI()