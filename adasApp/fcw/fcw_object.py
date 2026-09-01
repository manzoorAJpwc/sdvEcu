import cv2
import time
import csv
import sys
import os

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

def get_severity(ttc):
    if ttc < 0 or ttc > 4.0:
        return "None"
    if ttc > 2.5:
        return "Caution"
    if ttc > 1.5:
        return "Warning"
    return "Critical"

REFERENCE_WIDTH_PX = 150
REFERENCE_DISTANCE_M = 2.0

def estimate_distance(width_px):
    if width_px <= 0:
        return None
    return (REFERENCE_WIDTH_PX * REFERENCE_DISTANCE_M) / width_px

net = cv2.dnn.readNetFromCaffe(resource_path("MobileNetSSD_deploy.prototxt"), resource_path("MobileNetSSD_deploy.caffemodel"))
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle",
           "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse",
           "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
IGNORED_CLASSES = ["person"]
CONFIDENCE_THRESHOLD = 0.5

face_cascade = cv2.CascadeClassifier(resource_path('haarcascade_frontalface_default.xml'))

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
    exit()

print("Camera opened successfully.")
print("Press 'c' to toggle CAR ON/OFF.")
print("Press 'q' to quit.\n")

log = []
frame_count = 0
prev_distance = None
prev_time = None
car_on = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1
    (h, w) = frame.shape[:2]

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        car_on = not car_on
        state_text = "ON" if car_on else "OFF"
        color = GREEN if car_on else RED
        print(f"{color}[CAR STATE] Car turned {state_text}{RESET}")
        prev_distance = None
        prev_time = None
    elif key == ord('q'):
        break

    status_color = (0, 255, 0) if car_on else (0, 0, 255)
    cv2.putText(frame, f"CAR: {'ON' if car_on else 'OFF'}", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

    if not car_on:
        cv2.imshow("FCW - Forward Collision Warning", frame)
        continue

    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    current_time = time.time()
    best_box = None
    best_area = 0
    best_label = None

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx] if idx < len(CLASSES) else "object"

            if label in IGNORED_CLASSES:
                continue

            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (startX, startY, endX, endY) = box.astype("int")
            box_width = endX - startX
            box_area = box_width * (endY - startY)

            if box_area > best_area:
                best_area = box_area
                best_box = (startX, startY, endX, endY, box_width)
                best_label = label

    if best_box:
        (startX, startY, endX, endY, box_width) = best_box
        cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)
        cv2.putText(frame, best_label, (startX, startY - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        distance = estimate_distance(box_width)
        ttc = -1
        relative_speed = 0.0

        if prev_distance is not None and prev_time is not None:
            dt = current_time - prev_time
            if dt > 0:
                relative_speed = (distance - prev_distance) / dt
                if relative_speed < -0.05:
                    ttc = distance / abs(relative_speed)

        severity = get_severity(ttc)
        prev_distance = distance
        prev_time = current_time

        cv2.putText(frame, f"Distance: {distance:.2f}m | TTC: {ttc:.2f}s | {severity}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if severity in ("Warning", "Critical"):
            alert_color = (0, 0, 255) if severity == "Critical" else (0, 165, 255)
            cv2.putText(frame, f"FCW ALERT: {severity}!", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, alert_color, 3)
            print(f"{RED if severity == 'Critical' else YELLOW}[FCW ALERT] {severity} ({best_label}) - TTC: {ttc:.2f}s{RESET}")
    else:
        prev_distance = None
        prev_time = None

    if frame_count % 30 == 0:
        log.append({
            "frame": frame_count,
            "car_on": car_on,
            "object": best_label if best_box else None,
            "distance_m": round(distance, 2) if best_box else None,
            "ttc_s": round(ttc, 2) if best_box else None,
            "severity": severity if best_box else "None"
        })

    cv2.imshow("FCW - Forward Collision Warning", frame)

if log:
    with open("fcw_object_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log[0].keys())
        writer.writeheader()
        writer.writerows(log)
    print(f"\nSession complete. {len(log)} samples logged to fcw_object_log.csv")

cap.release()
cv2.destroyAllWindows()