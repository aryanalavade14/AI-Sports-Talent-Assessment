from extract import get_landmarks
from jump import jump_height

def analyze_jump(video_path, height_cm):
    data, fps = get_landmarks(video_path)
    return {"jump_cm": round(float(jump_height(data, fps, height_cm)), 1), "status": "ok"}

if __name__ == "__main__":
    print(analyze_jump("videos/test1.mp4", 170))