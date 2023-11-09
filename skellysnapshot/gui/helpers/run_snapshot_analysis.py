from skellysnapshot.backend.snapshot_analyzer import SnapshotAnalyzer


def run_analysis(snapshot, path_to_calibration_toml):
    snapshot_analyzer = SnapshotAnalyzer()
    snapshot_analyzer.run(snapshot, path_to_calibration_toml)

    # Assume snapshot_data is available here, replace with actual data
    snapshot_images = snapshot_analyzer.snapshot2d_data.annotated_images
    snapshot_data_3d = snapshot_analyzer.snapshot3d_data

    return snapshot_images, snapshot_data_3d
