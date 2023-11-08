import cv2
import numpy as np
import time
from collections import deque

event_queue = deque()
def capture_frames(capture_devices):
    frames = {}
    for i, cap in enumerate(capture_devices):
        ret, frame = cap.read()
        if ret:
            frames[f'cam_{i}'] = frame
    return frames

def show_in_one_window(frames, window_name='All Webcams'):
    num_frames = len(frames)
    if num_frames == 0:
        return

    # Convert dict values to a list
    frame_list = list(frames.values())

    # Concatenate frames horizontally
    concatenated_frame = np.hstack(frame_list)

    # Show in one OpenCV window
    cv2.imshow(window_name, concatenated_frame)

def main(snapshot_callback, settings_dict:dict):
    num_webcams = 2
    capture_devices = [cv2.VideoCapture(i) for i in range(num_webcams)]

    try:
        while True:
            # Check event queue
            current_time = time.time()
            if event_queue and event_queue[0]['time'] <= current_time:
                event = event_queue.popleft()
                if event['type'] == 'snapshot':
                    print("Snapshot captured")
                    snapshot = capture_frames(capture_devices)
                    if snapshot_callback is not None:
                        snapshot_callback(snapshot)

            # Capture and show frames
            frames = capture_frames(capture_devices)
            show_in_one_window(frames)

            # Check for 's' key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                print("Preparing to capture snapshot...")
                event_time = current_time + settings_dict['timer']  # 3 seconds into the future
                event = {'type': 'snapshot', 'time': event_time}
                event_queue.append(event)

            if key == ord('q'):
                break

    finally:
        for cap in capture_devices:
            cap.release()
        cv2.destroyAllWindows()


def snapshot_callback_test(snapshot):
    print(snapshot.keys())

if __name__ == "__main__":
    settings_dict = {
        'timer':0
    }
    main(snapshot_callback=snapshot_callback_test, settings_dict=settings_dict)
