from skellysnapshot.calibration.freemocap_anipose import CameraGroup 

class CalibrationState:
    def __init__(self):
        self.status = "NOT_LOADED"  # or use enums
        self.calibration_object = None

class ProcessEnableConditions:
    def __init__(self):
        self.conditions = {
            'calibration_loaded': False,
            # 'cameras_connected': False,
        }




class AppState:
    def __init__(self):
        self.calibration_state = CalibrationState()
        self.process_enable_conditions = ProcessEnableConditions()
        self.subscribers = {"calibration": []}

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


    def subscribe(self, topic, subscriber):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(subscriber)

    def notify_subscribers(self, topic, state_data):
        for subscriber in self.subscribers.get(topic, []):
            subscriber(state_data)
