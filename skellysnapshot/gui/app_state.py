from skellysnapshot.calibration.freemocap_anipose import CameraGroup 

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


class AppState:
    def __init__(self):
        self.calibration_state = CalibrationState()
        self.process_enable_conditions = ProcessEnableConditions()
        self.subscribers = {'calibration': [], 'enable_processing': []}

    def update_calibration_state(self, calibration_object=None):
        if not isinstance(calibration_object, CameraGroup):
            print(f"Invalid calibration object type. Must be of type CameraGroup, but is of type {type(calibration_object)}")
            return
        
        if calibration_object:
            self.calibration_state.calibration_object = calibration_object
            self.calibration_state.status = "LOADED"  # or use enums
        else:
            self.calibration_state.calibration_object = None
            self.calibration_state.status = "NOT_LOADED"  # or use enums
        self.notify_subscribers("calibration", self.calibration_state)

    def check_enable_conditions(self):
        all_conditions_met = all(self.process_enable_conditions.conditions.values())
        print(f"Checking enable conditions. All conditions met: {all_conditions_met}")
        print(f"Current condition states: {self.process_enable_conditions.conditions}")
        self.notify_subscribers("enable_processing", all_conditions_met)


    def update_button_enable_conditions(self, condition_name, condition_value):
        print(f"Received update for enabling snapshot processing: '{condition_name}' with value '{condition_value}'")
        self.process_enable_conditions.conditions[condition_name] = condition_value
        print(f"Updated conditions: {self.process_enable_conditions.conditions}")
        self.check_enable_conditions()

    def subscribe(self, topic, subscriber):
        print('Subscribing to topic: ', topic, ' Subscriber: ', subscriber)
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)

    def notify_subscribers(self, topic, state_data):
        for subscriber in self.subscribers.get(topic, []):
            subscriber(state_data)
