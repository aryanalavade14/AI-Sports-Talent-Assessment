from fastapi import FastAPI, UploadFile, Form
import shutil, os
from analyze import analyze_jump

app = FastAPI()

@app.post("/analyze-jump")
async def analyze(video: UploadFile, height_cm: float = Form(...)):
    if height_cm < 100 or height_cm > 230:
        return {"status": "error", "message": "Height must be between 100 and 230 cm"}
    path = f"temp_{video.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    try:
        return analyze_jump(path, height_cm)
    finally:
        os.remove(path)
