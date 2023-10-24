from skellysnapshot.calibration.freemocap_anipose import CameraGroup 

class CalibrationState:
    def __init__(self):
        self.status = "NOT_LOADED"  # or use enums
        self.calibration_object = None

class ProcessEnableConditions:
    def __init__(self):
        self.conditions = {
            'calibration_loaded': False,
            'cameras_connected': False  # You can add more conditions here
        }
        self.subscribers = []

    def subscribe(self, subscriber):
        print('Subscribing process enabling subscriber: ', subscriber)
        self.subscribers.append(subscriber)

    def notify_subscribers(self):
        print(f'Notifying process enabling subscribers {self.subscribers} of current conditions: {self.conditions}')
        for subscriber in self.subscribers:
            subscriber(self)


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

    def update_button_enable_conditions(self, condition_name, condition_value):
        print('Update recieved. Condition name: ', condition_name, ' Condition value: ', condition_value)
        self.process_enable_conditions.conditions[condition_name] = condition_value
        self.process_enable_conditions.notify_subscribers()

    def subscribe(self, topic, subscriber):
        print('Subscribing to topic: ', topic, ' Subscriber: ', subscriber)
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)

    def notify_subscribers(self, topic, state_data):
        for subscriber in self.subscribers.get(topic, []):
            subscriber(state_data)
