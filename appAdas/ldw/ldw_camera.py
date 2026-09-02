import cv2
import numpy as np
import csv
import sys
from pathlib import Path

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'


def get_drift_status(lateral_offset_ratio):
    abs_offset = abs(lateral_offset_ratio)

    if abs_offset < 0.15:
        return "Centered", "None"
    elif abs_offset < 0.35:
        direction = (
            "Drifting Left"
            if lateral_offset_ratio < 0
            else "Drifting Right"
        )
        return direction, "Caution"
    else:
        direction = (
            "Drifting Left"
            if lateral_offset_ratio < 0
            else "Drifting Right"
        )
        return direction, "Warning"


def detect_lane_lines(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)

    height, width = frame.shape[:2]

    roi_mask = np.zeros_like(edges)

    roi_vertices = np.array([
        [
            (0, height),
            (width, height),
            (width, int(height * 0.5)),
            (0, int(height * 0.5))
        ]
    ], dtype=np.int32)

    cv2.fillPoly(roi_mask, roi_vertices, 255)

    masked_edges = cv2.bitwise_and(edges, roi_mask)

    lines = cv2.HoughLinesP(
        masked_edges,
        1,
        np.pi / 180,
        threshold=50,
        minLineLength=50,
        maxLineGap=20
    )

    return lines, masked_edges


# ------------------------------------------
# Video input
# ------------------------------------------

if len(sys.argv) < 2:
    print("Usage:")
    print("    ldw_camera <video-file>")
    print("")
    print("Example:")
    print("    ldw_camera ../simRepo/adas/simDriver.mp4")
    sys.exit(1)

video_path = Path(sys.argv[1]).expanduser().resolve()

print(f"Opening video: {video_path}")

if not video_path.is_file():
    print(f"Video file not found: {video_path}")
    sys.exit(1)

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    print(f"Cannot open video: {video_path}")
    sys.exit(1)

print("Video opened successfully.")
print("Press 'c' to toggle car ON/OFF.")
print("Press 'q' to quit.\n")

log = []
frame_count = 0

# Start ON for simulation
car_on = True

while True:

    ret, frame = cap.read()

    if not ret:
        print("End of video. Restarting...")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame_count += 1

    height, width = frame.shape[:2]
    frame_center_x = width // 2

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        car_on = not car_on

        state_text = "ON" if car_on else "OFF"

        color = GREEN if car_on else RED

        print(
            f"{color}[CAR STATE] Car turned "
            f"{state_text}{RESET}"
        )

    elif key == ord('q'):
        break

    status_color = (0, 255, 0) if car_on else (0, 0, 255)

    cv2.putText(
        frame,
        f"CAR: {'ON' if car_on else 'OFF'}",
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2
    )

    if not car_on:
        cv2.imshow("LDW - Lane Departure Warning", frame)
        continue

    lines, masked_edges = detect_lane_lines(frame)

    lateral_offset_ratio = 0.0
    status = "No Lines Detected"
    severity = "None"

    if lines is not None and len(lines) > 0:

        left_lines_x = []
        right_lines_x = []

        for line in lines:

            coords = np.asarray(line).reshape(-1)

            if len(coords) < 4:
                continue

            x1, y1, x2, y2 = map(int, coords[:4])

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            mid_x = (x1 + x2) / 2

            if mid_x < frame_center_x:
                left_lines_x.append(mid_x)
            else:
                right_lines_x.append(mid_x)

        if left_lines_x and right_lines_x:

            lane_center_x = (
                np.mean(left_lines_x) +
                np.mean(right_lines_x)
            ) / 2

            lateral_offset_px = (
                frame_center_x - lane_center_x
            )

            lateral_offset_ratio = (
                lateral_offset_px / (width / 2)
            )

            status, severity = get_drift_status(
                lateral_offset_ratio
            )

        elif left_lines_x or right_lines_x:
            status = "Only One Line Detected"
            severity = "None"

    cv2.line(
        frame,
        (frame_center_x, height),
        (frame_center_x, int(height * 0.5)),
        (255, 255, 0),
        1
    )

    cv2.putText(
        frame,
        f"Offset: {lateral_offset_ratio:.2f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Status: {status}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    if severity in ("Caution", "Warning"):

        alert_color = (
            (0, 165, 255)
            if severity == "Caution"
            else (0, 0, 255)
        )

        cv2.putText(
            frame,
            f"LDW ALERT: {status}!",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            alert_color,
            3
        )

        print(
            f"{YELLOW if severity == 'Caution' else RED}"
            f"[LDW ALERT] {status} "
            f"- Offset: {lateral_offset_ratio:.2f}"
            f"{RESET}"
        )

    if frame_count % 30 == 0:
        log.append({
            "frame": frame_count,
            "car_on": car_on,
            "lateral_offset_ratio": round(
                lateral_offset_ratio,
                3
            ),
            "status": status,
            "severity": severity
        })

    cv2.imshow(
        "LDW - Lane Departure Warning",
        frame
    )

    cv2.imshow(
        "Edge Detection Debug",
        masked_edges
    )

if log:

    with open(
        "ldw_camera_log.csv",
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=log[0].keys()
        )

        writer.writeheader()
        writer.writerows(log)

    print(
        f"\nSession complete. "
        f"{len(log)} samples logged "
        f"to ldw_camera_log.csv"
    )

cap.release()
cv2.destroyAllWindows()