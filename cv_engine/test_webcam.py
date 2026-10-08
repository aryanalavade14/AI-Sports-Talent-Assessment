import cv2, mediapipe as mp

pose = mp.solutions.pose.Pose()
draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if res.pose_landmarks:
        draw.draw_landmarks(frame, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
    cv2.imshow("Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()