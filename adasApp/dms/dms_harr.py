import cv2
import time
import csv
import pyttsx3
import sys
import os
from collections import deque

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

WARNING_THRESHOLD = 1.0
EMERGENCY_THRESHOLD = 2.0
WINDOW_SIZE = 30
OPEN_RATIO_THRESHOLD = 0.3


def run_dms_session():
    """
    Runs the DMS detection loop using the laptop camera.
    Returns a summary string when the session ends (user presses 'q').
    """
    engine = pyttsx3.init()

    face_cascade = cv2.CascadeClassifier(resource_path('haarcascade_frontalface_default.xml'))
    eye_cascade = cv2.CascadeClassifier(resource_path('haarcascade_eye.xml'))

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "ERROR: Cannot access camera"

    print("Camera opened successfully. Press 'q' to quit.")

    eyes_closed_start_time = None
    warning_triggered = False
    emergency_triggered = False
    detection_history = deque(maxlen=WINDOW_SIZE)

    event_log = []

    def log_event(event_type, duration=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        event_log.append({"time": timestamp, "event": event_type, "duration_s": duration})
        color = RED if event_type == "EMERGENCY_ALERT" else YELLOW if event_type == "DROWSY_WARNING" else GREEN
        msg = f"[{timestamp}] EVENT: {event_type}"
        if duration:
            msg += f" (duration: {duration:.2f}s)"
        print(f"{color}{msg}{RESET}")

    frame_count = 0
    emergency_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(100, 100))

        eyes_detected_this_frame = False

        for (x, y, fw, fh) in faces:
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 0, 0), 2)
            roi_gray = gray[y:y + fh, x:x + fw]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 4, minSize=(15, 15))

            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
                eyes_detected_this_frame = True

        if len(faces) > 0:
            detection_history.append(1 if eyes_detected_this_frame else 0)
            open_ratio = sum(detection_history) / len(detection_history) if detection_history else 1.0
            genuinely_open = open_ratio >= OPEN_RATIO_THRESHOLD

            cv2.putText(frame, f"Open ratio: {open_ratio:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            if not genuinely_open:
                if eyes_closed_start_time is None:
                    eyes_closed_start_time = time.time()
                    log_event("EYES_CLOSED_STARTED")

                elapsed = time.time() - eyes_closed_start_time

                if elapsed >= WARNING_THRESHOLD and not warning_triggered:
                    log_event("DROWSY_WARNING", elapsed)
                    warning_triggered = True

                if elapsed >= WARNING_THRESHOLD:
                    cv2.putText(frame, f"DROWSY WARNING ({elapsed:.1f}s)", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                if elapsed >= EMERGENCY_THRESHOLD and not emergency_triggered:
                    log_event("EMERGENCY_ALERT", elapsed)
                    try:
                        engine.say("Wake up! You are feeling drowsy!")
                        engine.runAndWait()
                    except Exception as e:
                        print(f"[DEBUG] Voice failed: {e}")
                    emergency_triggered = True
                    emergency_count += 1

                if elapsed >= EMERGENCY_THRESHOLD:
                    cv2.putText(frame, "!!! DROWSINESS EMERGENCY !!!", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
            else:
                if eyes_closed_start_time is not None:
                    total_duration = time.time() - eyes_closed_start_time
                    log_event("EYES_REOPENED", total_duration)

                eyes_closed_start_time = None
                warning_triggered = False
                emergency_triggered = False
        else:
            detection_history.clear()

        cv2.imshow("DMS - Driver Monitoring System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    with open("dms_event_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "event", "duration_s"])
        writer.writeheader()
        writer.writerows(event_log)

    cap.release()
    cv2.destroyAllWindows()

    return f"DMS session complete. {len(event_log)} events logged. {emergency_count} emergency alert(s) triggered."


if __name__ == "__main__":
    result = run_dms_session()
    print(result)