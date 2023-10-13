import cv2
import numpy as np

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

def main(snapshot_callback=None):
    # Initialize webcams
    num_webcams = 2  # Change based on your setup
    capture_devices = [cv2.VideoCapture(i) for i in range(num_webcams)]

    try:
        while True:
            # Capture frames
            snapshot = capture_frames(capture_devices)

            # Show all in one window
            show_in_one_window(snapshot)

            # Capture a snapshot if 's' key is pressed
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                print("Snapshot captured")
                if snapshot_callback is not None:
                    snapshot_callback(snapshot)

            if key == ord('q'):
                break


    finally:
        # Release capture devices and close windows
        for cap in capture_devices:
            cap.release()
        cv2.destroyAllWindows()


def snapshot_callback_test(snapshot):
    print (snapshot.keys())

if __name__ == "__main__":
    main(snapshot_callback=snapshot_callback_test)
