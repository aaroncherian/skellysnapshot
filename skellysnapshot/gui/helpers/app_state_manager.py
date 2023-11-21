import logging

from skellysnapshot.backend.calibration.freemocap_anipose import CameraGroup


class CalibrationState:
    def __init__(self):
        self.status = "NOT_LOADED"  # or use enums
        self.calibration_object = None


class ProcessEnableConditions:
    def __init__(self):
        self.conditions = {
            'calibration_loaded': False,
            # 'cameras_connected': False  # You can add more conditions here
        }


class SnapshotState:
    def __init__(self):
        self.countdown_timer = 0  # Default value for countdown timer

    def update_countdown_timer(self, new_timer_value):
        self.countdown_timer = new_timer_value

class AppStateManager:
    def __init__(self):
        self.calibration_state = CalibrationState()
        self.process_enable_conditions = ProcessEnableConditions()
        self.snapshot_state = SnapshotState()
        self.subscribers = {'calibration': [], 'enable_processing': [], 'snapshot_settings': []}

    def check_initial_calibration_state(self):
        self.notify_subscribers("calibration", self.calibration_state)

    def update_calibration_state(self, calibration_object=None):
        if not isinstance(calibration_object, CameraGroup):
            logging.warning(
                f"Invalid calibration object type. Must be of type CameraGroup, but is of type {type(calibration_object)}")
            return

        if calibration_object:
            self.calibration_state.calibration_object = calibration_object
            self.calibration_state.status = "LOADED"  # or use enums
        else:
            self.calibration_state.calibration_object = None
            self.calibration_state.status = "NOT_LOADED"  # or use enums
        self.notify_subscribers("calibration", self.calibration_state)

    def update_snapshot_timer(self, new_timer_value):
        self.snapshot_state.update_countdown_timer(new_timer_value)
        logging.info(f"Countdown timer updated to {new_timer_value} seconds")
        self.notify_subscribers("snapshot", self.snapshot_state.countdown_timer)

    def check_enable_conditions(self):
        all_conditions_met = all(self.process_enable_conditions.conditions.values())
        logging.info(f"Checking enable conditions. All conditions met: {all_conditions_met}")
        logging.debug(f"Current condition states: {self.process_enable_conditions.conditions}")
        self.notify_subscribers("enable_processing", all_conditions_met)

    def update_button_enable_conditions(self, condition_name, condition_value):
        logging.info(
            f"Received update for enabling snapshot processing: '{condition_name}' with value '{condition_value}'")
        self.process_enable_conditions.conditions[condition_name] = condition_value
        logging.debug(f"Updated conditions: {self.process_enable_conditions.conditions}")
        self.check_enable_conditions()

    def subscribe(self, topic, subscriber):
        logging.info(f'Subscribing to topic: {topic}, Subscriber: {subscriber}')
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)

    def notify_subscribers(self, topic, state_data):
        for subscriber in self.subscribers.get(topic, []):
            subscriber(state_data)
