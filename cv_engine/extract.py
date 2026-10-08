import cv2, mediapipe as mp, numpy as np

def get_landmarks(path):
    pose = mp.solutions.pose.Pose(model_complexity=1)
    L = mp.solutions.pose.PoseLandmark
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    data = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        h, w, _ = frame.shape
        res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            hip_y = (lm[L.LEFT_HIP].y + lm[L.RIGHT_HIP].y) / 2 * h
            nose_y = lm[L.NOSE].y * h
            ankle_y = (lm[L.LEFT_ANKLE].y + lm[L.RIGHT_ANKLE].y) / 2 * h
            data.append([hip_y, nose_y, ankle_y])
        else:
            data.append([np.nan] * 3)
    cap.release()
    return np.array(data), fps
