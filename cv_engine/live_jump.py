import cv2, mediapipe as mp, numpy as np

HEIGHT_CM = 170  # change to your height

pose = mp.solutions.pose.Pose()
L = mp.solutions.pose.PoseLandmark
cap = cv2.VideoCapture(0)

hips, scale, baseline = [], None, None
print("Stand sideways, full body in view. Stay still for 3 seconds...")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    h, w, _ = frame.shape
    res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if res.pose_landmarks:
        lm = res.pose_landmarks.landmark
        hip = (lm[L.LEFT_HIP].y + lm[L.RIGHT_HIP].y) / 2 * h
        nose = lm[L.NOSE].y * h
        ankle = (lm[L.LEFT_ANKLE].y + lm[L.RIGHT_ANKLE].y) / 2 * h
        hips.append(hip)

        # after ~90 frames (about 3 sec), lock the baseline and scale
        if len(hips) == 90:
            baseline = np.median(hips)
            scale = (HEIGHT_CM * 0.93) / (ankle - nose)
            print("Calibrated! Now jump.")

        if baseline is not None:
            jump_cm = max(0, (baseline - hip) * scale)
            cv2.putText(frame, f"Jump: {jump_cm:.1f} cm", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        mp.solutions.drawing_utils.draw_landmarks(
            frame, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
    cv2.imshow("Live Jump", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release(); cv2.destroyAllWindows()