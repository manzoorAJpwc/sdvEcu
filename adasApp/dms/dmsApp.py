import cv2
import time
import csv
import sys
import os
from pathlib import Path
from collections import deque

# ============================================================
# Terminal colors
# ============================================================

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

# ============================================================
# Configuration
# ============================================================

WARNING_THRESHOLD = 1.0
EMERGENCY_THRESHOLD = 2.0

WINDOW_SIZE = 30
OPEN_RATIO_THRESHOLD = 0.3

# ============================================================
# Resource handling
# ============================================================

def resource_path(relative_path):
    """
    Works both in development and PyInstaller executable.
    """

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ============================================================
# Video input
# ============================================================

def get_video_path():

    if len(sys.argv) < 2:
        print("Usage:")
        print("    dmsApp <video-file>")
        print("")
        print("Example:")
        print("    dmsApp ../simRepo/adas/simDriver.mp4")
        sys.exit(1)

    video_path = Path(sys.argv[1]).expanduser().resolve()

    if not video_path.is_file():
        print(
            f"{RED}ERROR: Video file not found: "
            f"{video_path}{RESET}"
        )
        sys.exit(1)

    return video_path

# ============================================================
# Main DMS Session
# ============================================================

def run_dms_session(video_path):

    face_xml = resource_path(
        "haarcascade_frontalface_default.xml"
    )

    eye_xml = resource_path(
        "haarcascade_eye.xml"
    )

    print(f"Loading: {face_xml}")
    print(f"Loading: {eye_xml}")

    face_cascade = cv2.CascadeClassifier(face_xml)
    eye_cascade = cv2.CascadeClassifier(eye_xml)

    if face_cascade.empty():
        return (
            "ERROR: Failed to load "
            "haarcascade_frontalface_default.xml"
        )

    if eye_cascade.empty():
        return (
            "ERROR: Failed to load "
            "haarcascade_eye.xml"
        )

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return (
            f"ERROR: Cannot open video: "
            f"{video_path}"
        )

    print(f"Video opened: {video_path}")
    print("Press 'c' to toggle DMS ON/OFF")
    print("Press 'q' to quit")
    print()

    eyes_closed_start_time = None

    warning_triggered = False
    emergency_triggered = False

    detection_history = deque(
        maxlen=WINDOW_SIZE
    )

    frame_count = 0
    emergency_count = 0

    event_log = []

    dms_on = True

    def log_event(event_type, duration=None):

        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        event_log.append(
            {
                "time": timestamp,
                "event": event_type,
                "duration_s":
                    round(duration, 3)
                    if duration is not None
                    else ""
            }
        )

        if event_type == "EMERGENCY_ALERT":
            color = RED
        elif event_type == "DROWSY_WARNING":
            color = YELLOW
        else:
            color = GREEN

        msg = (
            f"[{timestamp}] EVENT: "
            f"{event_type}"
        )

        if duration is not None:
            msg += (
                f" (duration: "
                f"{duration:.2f}s)"
            )

        print(f"{color}{msg}{RESET}")

    try:

        while True:

            ret, frame = cap.read()

            if not ret:

                print(
                    "End of video reached."
                )

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                eyes_closed_start_time = None

                warning_triggered = False
                emergency_triggered = False

                detection_history.clear()

                continue

            frame_count += 1

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):

                dms_on = not dms_on

                state = (
                    "ON"
                    if dms_on
                    else "OFF"
                )

                color = (
                    GREEN
                    if dms_on
                    else RED
                )

                print(
                    f"{color}[DMS STATE] "
                    f"{state}{RESET}"
                )

                if not dms_on:

                    eyes_closed_start_time = None

                    warning_triggered = False
                    emergency_triggered = False

                    detection_history.clear()

            elif key == ord("q"):
                break

            height = frame.shape[0]

            state_color = (
                (0, 255, 0)
                if dms_on
                else (0, 0, 255)
            )

            cv2.putText(
                frame,
                f"DMS: {'ON' if dms_on else 'OFF'}",
                (10, height - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                state_color,
                2
            )

            if not dms_on:

                cv2.imshow(
                    "DMS - Driver Monitoring System",
                    frame
                )

                continue

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(100, 100)
            )

            eyes_detected_this_frame = False

            for (
                x,
                y,
                fw,
                fh
            ) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + fw, y + fh),
                    (255, 0, 0),
                    2
                )

                roi_gray = gray[
                    y:y + fh,
                    x:x + fw
                ]

                eyes = eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,
                    minNeighbors=4,
                    minSize=(15, 15)
                )

                for (
                    ex,
                    ey,
                    ew,
                    eh
                ) in eyes:

                    cv2.rectangle(
                        frame,
                        (x + ex, y + ey),
                        (
                            x + ex + ew,
                            y + ey + eh
                        ),
                        (0, 255, 0),
                        2
                    )

                    eyes_detected_this_frame = True

            if len(faces) > 0:

                detection_history.append(
                    1
                    if eyes_detected_this_frame
                    else 0
                )

                open_ratio = (
                    sum(detection_history)
                    / len(detection_history)
                )

                genuinely_open = (
                    open_ratio >= OPEN_RATIO_THRESHOLD
                )

                cv2.putText(
                    frame,
                    f"Open ratio: {open_ratio:.2f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )

                cv2.putText(
                    frame,
                    f"Eyes: {'YES' if eyes_detected_this_frame else 'NO'}",
                    (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1
                )

                if not genuinely_open:

                    if eyes_closed_start_time is None:

                        eyes_closed_start_time = (
                            time.time()
                        )

                        log_event(
                            "EYES_CLOSED_STARTED"
                        )

                    elapsed = (
                        time.time()
                        - eyes_closed_start_time
                    )

                    if (
                        elapsed >= WARNING_THRESHOLD
                        and not warning_triggered
                    ):

                        log_event(
                            "DROWSY_WARNING",
                            elapsed
                        )

                        warning_triggered = True

                    if elapsed >= WARNING_THRESHOLD:

                        cv2.putText(
                            frame,
                            f"DROWSY WARNING ({elapsed:.1f}s)",
                            (10, 85),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2
                        )

                    if (
                        elapsed >= EMERGENCY_THRESHOLD
                        and not emergency_triggered
                    ):

                        log_event(
                            "EMERGENCY_ALERT",
                            elapsed
                        )

                        emergency_triggered = True
                        emergency_count += 1

                    if elapsed >= EMERGENCY_THRESHOLD:

                        cv2.putText(
                            frame,
                            "!!! DROWSINESS EMERGENCY !!!",
                            (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 0, 255),
                            3
                        )

                else:

                    if (
                        eyes_closed_start_time
                        is not None
                    ):

                        closed_duration = (
                            time.time()
                            - eyes_closed_start_time
                        )

                        log_event(
                            "EYES_REOPENED",
                            closed_duration
                        )

                    eyes_closed_start_time = None

                    warning_triggered = False
                    emergency_triggered = False

            else:

                detection_history.clear()

                eyes_closed_start_time = None

                warning_triggered = False
                emergency_triggered = False

                cv2.putText(
                    frame,
                    "No face detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 165, 255),
                    2
                )

            cv2.imshow(
                "DMS - Driver Monitoring System",
                frame
            )

    finally:

        log_file = (
            Path.cwd()
            / "dms_event_log.csv"
        )

        with open(
            log_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "time",
                    "event",
                    "duration_s"
                ]
            )

            writer.writeheader()
            writer.writerows(
                event_log
            )

        cap.release()
        cv2.destroyAllWindows()

    return (
        f"DMS session complete. "
        f"{len(event_log)} events logged. "
        f"{emergency_count} emergency alert(s) triggered. "
        f"Log saved to dms_event_log.csv"
    )

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    video_path = get_video_path()

    result = run_dms_session(
        video_path
    )

    print(result)