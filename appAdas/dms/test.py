import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
import pyttsx3
from scipy.spatial import distance

# =====================================================
# VOICE ENGINE
# =====================================================

try:
    engine = pyttsx3.init()
    tts_available = True
    print("TTS Engine Initialized")
except Exception as e:
    print("TTS Initialization Failed:", e)
    tts_available = False

# =====================================================
# SETTINGS
# =====================================================

EAR_THRESHOLD = 0.22

WARNING_TIME = 3      # seconds
EMERGENCY_TIME = 5    # seconds

# =====================================================
# COLORS
# =====================================================

GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)

# =====================================================
# EAR CALCULATION
# =====================================================

def calculate_ear(eye):

    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])

    return (A + B) / (2.0 * C)

# =====================================================
# MEDIAPIPE EYE LANDMARKS
# =====================================================

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# =====================================================
# GET EYE POINTS
# =====================================================

def get_eye_points(landmarks, indices, width, height):

    points = []

    for idx in indices:
        x = int(landmarks[idx].x * width)
        y = int(landmarks[idx].y * height)
        points.append((x, y))

    return np.array(points)

# =====================================================
# ALARM FUNCTION
# =====================================================

def speak(text):

    try:
        if tts_available:
            engine.say(text)
            engine.runAndWait()
        else:
            winsound.Beep(2500, 1000)

    except Exception as e:
        print("Voice Error:", e)
        winsound.Beep(2500, 1000)

# =====================================================
# MEDIAPIPE FACEMESH
# =====================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# =====================================================
# CAMERA
# =====================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot Access Camera")
    exit()

print("=" * 50)
print("Driver Monitoring System Started")
print("Press Q to Exit")
print("=" * 50)

# =====================================================
# VARIABLES
# =====================================================

eyes_closed_start = None

warning_triggered = False
emergency_triggered = False

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    success, frame = cap.read()

    if not success:
        print("Failed to Read Camera Frame")
        break

    height, width, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:

        face_landmarks = results.multi_face_landmarks[0]
        landmarks = face_landmarks.landmark

        # -----------------------------------------
        # GET EYE LANDMARKS
        # -----------------------------------------

        left_eye = get_eye_points(
            landmarks,
            LEFT_EYE,
            width,
            height
        )

        right_eye = get_eye_points(
            landmarks,
            RIGHT_EYE,
            width,
            height
        )

        # -----------------------------------------
        # DRAW EYE POINTS
        # -----------------------------------------

        for point in left_eye:
            cv2.circle(frame, point, 2, GREEN, -1)

        for point in right_eye:
            cv2.circle(frame, point, 2, GREEN, -1)

        # -----------------------------------------
        # EAR
        # -----------------------------------------

        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)

        ear = (left_ear + right_ear) / 2

        cv2.putText(
            frame,
            f"EAR: {ear:.3f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            GREEN,
            2
        )

        # Uncomment for debugging
        # print(f"EAR = {ear:.3f}")

        # -----------------------------------------
        # DROWSINESS DETECTION
        # -----------------------------------------

        if ear < EAR_THRESHOLD:

            if eyes_closed_start is None:

                eyes_closed_start = time.time()

                print("Eyes Closed Detected")

            elapsed = time.time() - eyes_closed_start

            cv2.putText(
                frame,
                f"Closed: {elapsed:.1f}s",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                RED,
                2
            )

            # -------------------------------------
            # WARNING
            # -------------------------------------

            if elapsed >= WARNING_TIME and not warning_triggered:

                print("DROWSY WARNING")

                winsound.Beep(1500, 500)

                speak(
                    "Warning. Driver appears drowsy."
                )

                warning_triggered = True

            if elapsed >= WARNING_TIME:

                cv2.putText(
                    frame,
                    "DROWSINESS DETECTED",
                    (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    YELLOW,
                    3
                )

            # -------------------------------------
            # EMERGENCY
            # -------------------------------------

            if elapsed >= EMERGENCY_TIME and not emergency_triggered:

                print("EMERGENCY ALERT")

                winsound.Beep(2500, 1500)

                speak(
                    "Wake up immediately. Emergency alert."
                )

                emergency_triggered = True

            if elapsed >= EMERGENCY_TIME:

                cv2.putText(
                    frame,
                    "EMERGENCY ALERT",
                    (20, 190),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    RED,
                    4
                )

        else:

            eyes_closed_start = None
            warning_triggered = False
            emergency_triggered = False

            cv2.putText(
                frame,
                "Eyes Open",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                GREEN,
                2
            )

    else:

        eyes_closed_start = None

        cv2.putText(
            frame,
            "NO FACE DETECTED",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            RED,
            2
        )

    cv2.imshow(
        "Driver Monitoring System",
        frame
    )

    key = cv2.waitKey(1)

    if key & 0xFF == ord("q"):
        break

# =====================================================
# CLEANUP
# =====================================================

cap.release()

cv2.destroyAllWindows()

if tts_available:
    engine.stop()

print("System Closed")