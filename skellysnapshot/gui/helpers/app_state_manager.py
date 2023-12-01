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

class SnapshotSettings:
    DEFAULT_COUNTDOWN_TIMER = 0
    DEFAULT_NUM_SNAPSHOTS = 1
    DEFAULT_SNAPSHOT_INTERVAL = 500
    def __init__(self, countdown_timer=DEFAULT_COUNTDOWN_TIMER, num_snapshots=DEFAULT_NUM_SNAPSHOTS, snapshot_interval=DEFAULT_SNAPSHOT_INTERVAL):
        self.countdown_timer = countdown_timer
        self.num_snapshots = num_snapshots
        self.snapshot_interval = snapshot_interval

    def update(self, countdown_timer=None, num_snapshots=None, snapshot_interval=None):
        if countdown_timer is not None:
            self.countdown_timer = countdown_timer
        if num_snapshots is not None:
            self.num_snapshots = num_snapshots
        if snapshot_interval is not None:
            self.snapshot_interval = snapshot_interval
class AppStateManager:
    def __init__(self):
        self.calibration_state = CalibrationState()
        self.process_enable_conditions = ProcessEnableConditions()
        self.snapshot_settings = SnapshotSettings()
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

    def update_snapshot_settings(self, countdown_timer=None, num_snapshots=None, snapshot_interval=None):
        self.snapshot_settings.update(countdown_timer, num_snapshots, snapshot_interval)
        logging.info(f"Updating snapshot settings: Countdown Timer={self.snapshot_settings.countdown_timer}, Num Snapshots={self.snapshot_settings.num_snapshots}, Snapshot Interval={self.snapshot_settings.snapshot_interval}")
        self.notify_subscribers("snapshot_settings", self.snapshot_settings)

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
