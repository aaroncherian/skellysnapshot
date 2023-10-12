from pathlib import Path
import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

mediapipe_parameters = {
    'model_complexity': 2,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'static_image_mode': False,
}

def process_image(image, holistic_tracker):
    results = holistic_tracker.process(image)
    
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    
    return image, results

holistic_tracker = mp_holistic.Holistic(
    model_complexity=mediapipe_parameters['model_complexity'],
    min_detection_confidence=mediapipe_parameters['min_detection_confidence'],
    min_tracking_confidence=mediapipe_parameters['min_tracking_confidence'],
)

if __name__ == '__main__':

    input_video_path = Path(r"D:\2023-05-17_MDN_NIH_data\1.0_recordings\calib_3\sesh_2023-05-17_13_48_44_MDN_treadmill_2\synchronized_videos\sesh_2023-05-17_13_48_44_treadmill_2_synced_Cam3.mp4")
    output_video_path = Path(r'C:\Users\aaron\Documents\HumonLab\SkellySnapshot\test1.mp4')

    cap = cv2.VideoCapture(str(input_video_path))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_video_path), fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

    # Initialize frame counter
    current_frame = 0

    # Specify the range of frames you want to process
    start_frame = 450  # Change this to your desired start frame
    end_frame = 450  # Change this to your desired end frame

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Video stream has ended.")
            break

        annotated_frame, _ = process_image(frame, holistic_tracker)
        out.write(annotated_frame)
        current_frame += 1

        # Break the loop if end_frame is reached
        if current_frame > (end_frame - start_frame):
            print(f"Processed up to frame {end_frame}. Stopping.")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()