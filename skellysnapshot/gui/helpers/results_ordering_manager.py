from PySide6.QtCore import Signal, QObject

import logging

class ResultsOrderingManager(QObject):
    results_ready_to_display = Signal(int, object, object, object)

    def __init__(self):
        super().__init__()
        self.results_buffer = {}
        self.next_expected_id = 0
        self.logger = logging.getLogger(__name__)

    def process_results(self, snapshot_id, snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data):
        self.logger.info(f"Received results for snapshot ID {snapshot_id}")
        if snapshot_id == self.next_expected_id:
            self.logger.info(f"Displaying results for expected snapshot ID {snapshot_id}")
            self.results_ready_to_display.emit(snapshot_id, snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data)
            self.next_expected_id += 1
            self.process_buffered_results()
        else:
            self.logger.info(f"Buffering out-of-sequence results for snapshot ID {snapshot_id}")
            self.results_buffer[snapshot_id] = (snapshot2d_data, snapshot3d_data, snapshot_center_of_mass_data)

    def process_buffered_results(self):
        while self.next_expected_id in self.results_buffer:
            self.logger.info(f"Processing buffered results for snapshot ID {self.next_expected_id}")
            data = self.results_buffer.pop(self.next_expected_id)
            self.results_ready_to_display.emit(self.next_expected_id, *data)
            self.next_expected_id += 1