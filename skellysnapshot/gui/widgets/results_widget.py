import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget,QVBoxLayout, QPushButton, QGroupBox, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QImage, QPixmap

from skellysnapshot.gui.widgets.skeleton_view_widget import SkeletonViewWidget
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene
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

        zoom_dialog.setLayout(layout)
        zoom_dialog.exec()


class ResultsViewWidget(QWidget):
    def __init__(self, snapshot_images, snapshot_data_3d):
        super().__init__()
        layout = QHBoxLayout()

        # Create a QGridLayout for the images
        grid_layout = QGridLayout()

        row = 0
        col = 0

        for name, image in snapshot_images.items():
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

            # Add the label to the grid layout
            grid_layout.addWidget(label, row, col)

            # Update row and column for next image
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Add the grid layout to the main layout
        layout.addLayout(grid_layout)

        skeleton_view = SkeletonViewWidget('3d plot')
        skeleton_view.setMinimumSize(600, 600)
        skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
        layout.addWidget(skeleton_view)

        self.setLayout(layout)



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
