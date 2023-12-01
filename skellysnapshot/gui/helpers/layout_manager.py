from PySide6.QtWidgets import QTabWidget

from skellysnapshot.gui.widgets.results_widget import ResultsViewWidget


class LayoutManager:
    def __init__(self):
        self.tab_widget = QTabWidget()
        self.tab_indices = {}
        self.results_tab = None
        # self.results_tab_counter = 0

    def register_tab(self, tab, name):
        tab_index = self.tab_widget.addTab(tab, name)
        self.tab_indices[name] = tab_index

    # def initialize_layout(self):
    #     self.main_menu = MainMenu()
    #     self.tab_widget.addTab(self.main_menu, "Main Menu")

    #     self.camera_tab = CameraMenu()
    #     self.tab_widget.addTab(self.camera_tab, "Cameras")

    def add_results_tab(self, snapshot_2d_data, snapshot_3d_data, snapshot_center_of_mass_data):
        self.results_tab = ResultsViewWidget(snapshot_2d_data, snapshot_3d_data, snapshot_center_of_mass_data)
        # self.results_tab_counter += 1
        new_tab_index = self.tab_widget.addTab(self.results_tab, f"Snapshot {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(new_tab_index)
        self.results_tab.return_to_snapshot_tab_signal.connect(self.switch_to_camera_tab)

    def switch_to_calibration_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_indices['Calibration'])

    def switch_to_camera_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_indices['Cameras'])

    def switch_to_main_menu_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_indices['Main Menu'])
