import numpy as np
from extract import get_landmarks
from jump import jump_height

def analyze_jump(video_path, height_cm):
    try:
        data, fps = get_landmarks(video_path)
    except Exception:
        return {"status": "error", "message": "Could not read the video"}

    if len(data) == 0 or not fps:
        return {"status": "error", "message": "Video is empty or unreadable"}

    if len(data) < fps * 3:
        return {"status": "error", "message": "Video too short. Record at least 3 seconds"}

    seen = np.sum(~np.isnan(data[:, 0])) / len(data)
    if seen < 0.6:
        return {"status": "error", "message": "Person not clearly visible. Keep full body in frame"}

    jump = float(jump_height(data, fps, height_cm))
    if jump < 3:
        return {"status": "error", "message": "No jump detected"}
    if jump > 100:
        return {"status": "error", "message": "Result looks unrealistic. Please re-record"}

    return {"status": "ok", "jump_cm": round(jump, 1)}

if __name__ == "__main__":
    print(analyze_jump("videos/test1.mp4", 170))
