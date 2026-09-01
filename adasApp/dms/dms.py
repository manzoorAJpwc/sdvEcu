import cv2
import pyttsx3
import time

# ---- Initialize text-to-speech engine ----
engine = pyttsx3.init()

def speak_alert(message):
    engine.say(message)
    engine.runAndWait()

# ---- Constants ----
CLOSED_DURATION_THRESHOLD = 1.5  # seconds of continuous closure to trigger alert

# ---- Load Haar Cascade classifiers (local files, downloaded from GitHub) ----
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# ---- Open camera ----
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot access camera")
    exit()

print("Camera opened successfully. Press 'q' to quit.")

eyes_closed_start_time = None
alert_triggered = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(100, 100))

    eyes_detected = False

    for (x, y, fw, fh) in faces:
        cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 0, 0), 2)
        roi_gray = gray[y:y + fh, x:x + fw]

        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 4, minSize=(20, 20))

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
            eyes_detected = True

    if len(faces) > 0 and not eyes_detected:
        # Face found, but no eyes detected = likely closed
        if eyes_closed_start_time is None:
            eyes_closed_start_time = time.time()
        else:
            elapsed = time.time() - eyes_closed_start_time
            cv2.putText(frame, f"Eyes closed: {elapsed:.1f}s", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if elapsed >= CLOSED_DURATION_THRESHOLD and not alert_triggered:
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
                print(f"[ALERT] Eyes closed for {elapsed:.2f} seconds — EMERGENCY STATUS")
                speak_alert("Wake up! You are feeling drowsy!")
                alert_triggered = True
    else:
        eyes_closed_start_time = None
        alert_triggered = False

    cv2.imshow("DMS - Driver Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()