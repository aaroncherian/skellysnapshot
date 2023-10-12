import mediapipe as mp

from skellysnapshot.pose_estimation_2d.mediapipe_things.mediapipe_array_building import \
    convert_mediapipe_results_to_numpy_arrays

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def process_image(image, holistic_tracker):
    """Process a single image using the MediaPipe Holistic model.

    Args:
        image (np.array): The image to process.
        holistic_tracker (mp.solutions.Holistic): The MediaPipe Holistic model.

    Returns:
        results (mp.solutions.Holistic): The MediaPipe Holistic model results.
    """

    results = holistic_tracker.process(image)

    annotated_image = annotate_image(processed_image=image, mediapipe_results=results)

    image_height, image_width = image.shape[:2]
    mediapipe_landmark_dataclass = convert_mediapipe_results_to_numpy_arrays(mediapipe_results=results,
                                                                             image_width=image_width,
                                                                             image_height=image_height)

    # # drawing the landmarks back on the image as a check
    # for landmark in landmark_data.pose_landmarks[0]:
    #     x, y = int(landmark[0]), int(landmark[1])
    #     cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Draw green circle

    # cv2.imshow('Annotated Image', image)
    # cv2.waitKey(0)

    # f = 2

    return mediapipe_landmark_dataclass, annotated_image


def annotate_image(processed_image, mediapipe_results):
    # Draw the landmarks on the image
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(processed_image, mediapipe_results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    # Show the annotated image
    # cv2.imshow('Annotated Image', processed_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    annotated_image = processed_image
    return annotated_image


