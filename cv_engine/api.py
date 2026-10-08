from fastapi import FastAPI, UploadFile, Form
import shutil, os
from analyze import analyze_jump

app = FastAPI()

@app.post("/analyze-jump")
async def analyze(video: UploadFile, height_cm: float = Form(...)):
    path = f"temp_{video.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    result = analyze_jump(path, height_cm)
    os.remove(path)
    return result