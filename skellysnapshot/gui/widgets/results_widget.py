import cv2
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QImage, QPixmap

from skellysnapshot.gui.widgets.skeleton_view_widget import SkeletonViewWidget
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene,  QSizePolicy, QSpacerItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene

class ClickableImageLabel(QLabel):
    def __init__(self, scaled_pixmap, original_pixmap):
        super().__init__()
        self.original_pixmap = original_pixmap  # Store the original QPixmap
        self.setPixmap(scaled_pixmap)  # Set the scaled QPixmap for display

    def mousePressEvent(self, event):
        zoom_dialog = QDialog(self)
        zoom_dialog.setWindowTitle("Zoomed Image")
        layout = QVBoxLayout()

        graphics_view = QGraphicsView()
        scene = QGraphicsScene()

        # Use the original QPixmap for zoomed view
        scene.addPixmap(self.original_pixmap)
        graphics_view.setScene(scene)

        layout.addWidget(graphics_view)

        # Set the dialog size to be slightly larger than the image
        img_width = self.original_pixmap.width()
        img_height = self.original_pixmap.height()
        zoom_dialog.resize(img_width + 10, img_height + 10)  # Add a small margin

        zoom_dialog.setLayout(layout)
        zoom_dialog.exec()



class ResultsViewWidget(QWidget):
    return_to_snapshot_tab_signal = pyqtSignal()
    def __init__(self, snapshot_data_2d, snapshot_data_3d,snapshot_center_of_mass_data):
        super().__init__()
        layout = QVBoxLayout()

        self.create_annotated_images_groupbox(layout, snapshot_data_2d)
        self.create_skeleton_plot_groupbox(layout, snapshot_data_3d,snapshot_center_of_mass_data)
        self.add_return_to_snapshot_tab_button(layout)
        # self.create_skeleton_plot_groupbox(layout, snapshot_data_3d,snapshot_center_of_mass_data)
        # skeleton_view = SkeletonViewWidget('3d plot')
        # skeleton_view.setMinimumSize(600, 400)
        # skeleton_view.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
        # skeleton_view.plot_center_of_mass(snapshot_center_of_mass_data)
        # layout.addWidget(skeleton_view)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)


        self.setLayout(layout)


    def create_annotated_images_groupbox(self, layout, snapshot_data_2d):
        annotated_images_groupbox = QGroupBox("Annotated Images")
        annotated_images_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        annotated_images_layout = QGridLayout()
        row = 0
        col = 0
        
        for name, image in snapshot_data_2d.annotated_images.items():
            # Convert the image to be compatible with PyQt6
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            original_pixmap = QPixmap.fromImage(qt_image)  # Store the original QPixmap

            # Scale the pixmap
            scaled_pixmap = original_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)

            # Create a ClickableImageLabel to hold the image
            label = ClickableImageLabel(scaled_pixmap, original_pixmap)  # Pass both pixmaps
            # label.setObjectName('ResultsAnnotatedImageLabel')

            # Add the label to the grid layout
            annotated_images_layout.addWidget(label, row, col)

            # Update row and column for next image
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        annotated_images_groupbox.setLayout(annotated_images_layout)
        layout.addWidget(annotated_images_groupbox)


    def create_skeleton_plot_groupbox(self, layout, snapshot_data_3d,snapshot_center_of_mass_data):
        skeleton_plot_groupbox = QGroupBox("3D Reconstruction")
        skeleton_plot_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        skeleton_plot_layout = QVBoxLayout()

        skeleton_view = SkeletonViewWidget()
        skeleton_view.setMinimumSize(600, 400)
        skeleton_view.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
        skeleton_view.plot_center_of_mass(snapshot_center_of_mass_data)
        skeleton_plot_layout.addWidget(skeleton_view)

        skeleton_plot_groupbox.setLayout(skeleton_plot_layout)
        layout.addWidget(skeleton_plot_groupbox)

    def add_return_to_snapshot_tab_button(self,layout):
        self.button = QPushButton("Take Another Snapshot")
        self.button.clicked.connect(self.emit_return_to_snapshot_tab_signal)
        layout.addWidget(self.button)

    def emit_return_to_snapshot_tab_signal(self):
        self.return_to_snapshot_tab_signal.emit()

    
def add_snapshot_tab(tab_widget, snapshot_images, snapshot_data_3d):
    # Create a new tab widget
    new_tab = QWidget()
    main_layout = QHBoxLayout()

    label_layout = QVBoxLayout()



    for name, image in snapshot_images.items():
        # Convert the image to be compatible with PyQt6
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # Create a QLabel to hold the image
        label = QLabel()
        label.setPixmap(pixmap)
        label_layout.addWidget(label)

    skeleton_view = SkeletonViewWidget('3d plot')
    skeleton_view.setMinimumSize(600, 600)
    skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
    main_layout.addLayout(label_layout)
    main_layout.addWidget(skeleton_view)

    main_layout.addLayout(label_layout)
        

    # Add the layout to the tab
    new_tab.setLayout(main_layout)
    new_tab.adjustSize()
    new_tab_index = tab_widget.addTab(new_tab, f"Snapshot {tab_widget.count() + 1}")
    tab_widget.setCurrentIndex(new_tab_index)
