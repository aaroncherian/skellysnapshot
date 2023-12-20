import cv2
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QDialog, QVBoxLayout, QGraphicsView, QWidget, QGraphicsScene, QSpacerItem, \
    QSizePolicy, QGroupBox, QGridLayout, QPushButton, QHBoxLayout

from skellysnapshot.gui.widgets.skeleton_view_widget import SkeletonViewWidget


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


class GeneratedResultsViewWidget(QWidget):
    def __init__(self, snapshot_data_2d=None, snapshot_data_3d=None, snapshot_center_of_mass_data=None):
        super().__init__()
        layout = QHBoxLayout()

        # Create annotated images groupbox, initially empty
        self.images_layout = QGridLayout()
        self.create_annotated_images_groupbox(layout)

        # Create skeleton plot groupbox, initially empty
        self.skeleton_view = SkeletonViewWidget()
        self.skeleton_view.setMinimumSize(600, 400)
        self.create_skeleton_plot_groupbox(layout)

        # self.create_annotated_images_groupbox(layout, snapshot_data_2d)
        # self.create_skeleton_plot_groupbox(layout, snapshot_data_3d, snapshot_center_of_mass_data)
        self.add_return_to_snapshot_tab_button(layout)


        self.skeleton_view = SkeletonViewWidget()
        self.skeleton_view.setMinimumSize(600, 400)
        self.skeleton_view.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.create_skeleton_plot_groupbox(layout, snapshot_data_3d, snapshot_center_of_mass_data)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        self.setLayout(layout)

    def create_annotated_images_groupbox(self, layout, snapshot_data_2d):
        annotated_images_groupbox = QGroupBox("Annotated Images")
        annotated_images_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # This is the overall layout for the group box
        groupbox_layout = QVBoxLayout()

        # Create the explanatory label
        explanation_label = QLabel()
        explanation_label.setObjectName('ExplanationLabel')
        refined_explanation_text = """
        <p><strong>Annotated Camera Images:</strong><br>
        The images below are captured snapshots from each camera setup. They have been processed through the MediaPipe pose estimation algorithm to identify and track joint positions in two dimensions. The detected joints are illustrated with overlaid markers.</p>
        <p>To examine the details, please <strong>click on any image to enlarge it.</strong></p>
        """
        explanation_label.setText(refined_explanation_text)
        explanation_label.setWordWrap(True)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Add the explanatory label to the group box's overall layout
        groupbox_layout.addWidget(explanation_label)

        # Create a grid layout for the images
        images_layout = QGridLayout()

        row = 0
        col = 0

        for name, image in snapshot_data_2d.annotated_images.items():
            # Convert the image to be compatible with PyQt6
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            original_pixmap = QPixmap.fromImage(qt_image)

            # Scale the pixmap
            scaled_pixmap = original_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)

            # Create a ClickableImageLabel to hold the image
            image_label = ClickableImageLabel(scaled_pixmap, original_pixmap)  # Pass both pixmaps

            # Add the label to the grid layout
            images_layout.addWidget(image_label, row, col)

            # Update row and column for next image
            col += 1
            if col > 1:  # Assuming 2 columns here, adjust as needed
                col = 0
                row += 1

        # Add the grid layout to the group box's overall layout
        groupbox_layout.addLayout(images_layout)

        # Set the group box's layout to the QVBoxLayout
        annotated_images_groupbox.setLayout(groupbox_layout)

        # Add the group box to the parent layout
        layout.addWidget(annotated_images_groupbox)

    def create_skeleton_plot_groupbox(self, layout, snapshot_data_3d, snapshot_center_of_mass_data):
        skeleton_plot_groupbox = QGroupBox("3D Reconstruction")
        skeleton_plot_groupbox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        skeleton_plot_layout = QVBoxLayout()

        explanation_label = QLabel()
        explanation_label.setObjectName('ExplanationLabel')
        explanation_text = """
        <p><strong>3D Skeletal Reconstruction:</strong><br>
        This visualization represents the 3D reconstruction of the subject's pose, as captured from multiple camera angles. The system triangulates the position of each joint in three-dimensional space. Total body center of mass is also calculated and displayed.</p>
        <p>Explore the model by rotating and zooming in on the plot to study the pose in detail.</p>
        """
        explanation_label.setText(explanation_text)
        explanation_label.setWordWrap(True)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        skeleton_plot_layout.addWidget(explanation_label)

        skeleton_view = SkeletonViewWidget()
        skeleton_view.setMinimumSize(600, 400)
        skeleton_view.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        skeleton_view.plot_frame_of_3d_skeleton(snapshot_data_3d)
        skeleton_view.plot_center_of_mass(snapshot_center_of_mass_data)
        skeleton_plot_layout.addWidget(skeleton_view)

        # Add the explanatory text label under the 3D plot

        skeleton_plot_groupbox.setLayout(skeleton_plot_layout)
        layout.addWidget(skeleton_plot_groupbox)
    
    def update_results(self, new_snapshot_data_2d, new_snapshot_data_3d, new_snapshot_center_of_mass_data):
        # Update annotated images
        self.update_annotated_images(new_snapshot_data_2d)

        # Update 3D plot
        self.skeleton_view.update_3d_skeleton(new_snapshot_data_3d)
        self.skeleton_view.update_center_of_mass(new_snapshot_center_of_mass_data)

    def add_return_to_snapshot_tab_button(self, layout):
        self.button = QPushButton("Take Another Snapshot")
        self.button.clicked.connect(self.emit_return_to_snapshot_tab_signal)
        layout.addWidget(self.button)

    def emit_return_to_snapshot_tab_signal(self):
        self.return_to_snapshot_tab_signal.emit()

    def update_annotated_images(self, new_snapshot_data_2d):
        # Clear existing images from the layout if any
        for i in reversed(range(self.images_layout.count())): 
            self.images_layout.itemAt(i).widget().setParent(None)

        # Add new images to the layout
        row = 0
        col = 0
        for name, image in new_snapshot_data_2d.annotated_images.items():
            qt_image, original_pixmap, scaled_pixmap = self.convert_image_for_display(image)
            image_label = ClickableImageLabel(scaled_pixmap, original_pixmap)
            self.images_layout.addWidget(image_label, row, col)
            col += 1
            if col > 1:  # Assuming 2 columns here, adjust as needed
                col = 0
                row += 1

    def convert_image_for_display(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        qt_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        original_pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = original_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        return qt_image, original_pixmap, scaled_pixmap

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
