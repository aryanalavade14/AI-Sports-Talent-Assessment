from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
import shutil, os
from analyze import analyze_jump

app = FastAPI(
    title="Sports Talent AI/CV Engine",
    description="Measures vertical jump height (cm) from a side-view video using MediaPipe Pose. Send a video and the athlete height in cm. Returns jump_cm, or an error message.",
    version="1.0",
)

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Vertical Jump Analyzer</title>
<style>
  body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0;
         display: flex; justify-content: center; padding-top: 60px; }
  .card { background: #1e293b; padding: 32px; border-radius: 16px; width: 360px; }
  h1 { font-size: 22px; margin-top: 0; }
  label { display: block; margin-top: 16px; font-size: 14px; color: #94a3b8; }
  input { width: 100%; margin-top: 6px; padding: 8px; border-radius: 8px;
          border: 1px solid #334155; background: #0f172a; color: #e2e8f0; box-sizing: border-box; }
  button { margin-top: 24px; width: 100%; padding: 12px; border: none; border-radius: 8px;
           background: #22c55e; color: #052e16; font-size: 16px; font-weight: bold; cursor: pointer; }
  #out { margin-top: 24px; font-size: 28px; font-weight: bold; text-align: center; }
  .small { font-size: 12px; color: #64748b; text-align: center; margin-top: 16px; }
</style>
</head>
<body>
<div class="card">
  <h1>Vertical Jump Analyzer</h1>
  <label>Jump video (side view, full body)</label>
  <input type="file" id="v" accept="video/*">
  <label>Athlete height (cm)</label>
  <input type="number" id="h" placeholder="e.g. 170">
  <button onclick="go()">Analyze</button>
  <div id="out"></div>
  <div class="small">API docs: <a href="/docs" style="color:#94a3b8">/docs</a></div>
</div>
<script>
async function go() {
  const f = document.getElementById('v').files[0];
  const h = document.getElementById('h').value;
  const out = document.getElementById('out');
  if (!f || !h) { out.textContent = 'Pick a video and enter height'; return; }
  out.textContent = 'Analyzing... (10-15 sec)';
  const fd = new FormData();
  fd.append('video', f);
  fd.append('height_cm', h);
  try {
    const r = await fetch('/analyze-jump', { method: 'POST', body: fd });
    const d = await r.json();
    out.textContent = d.status === 'ok' ? d.jump_cm + ' cm' : 'Error: ' + d.message;
  } catch (e) {
    out.textContent = 'Could not reach the server';
  }
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return PAGE

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/analyze-jump")
async def analyze(video: UploadFile, height_cm: float = Form(...)):
    """Send a video file and the athlete height in cm.
    Returns {"status": "ok", "jump_cm": 42.5} or {"status": "error", "message": "..."}"""
    if height_cm < 100 or height_cm > 230:
        return {"status": "error", "message": "Height must be between 100 and 230 cm"}
    path = f"temp_{video.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    try:
        return analyze_jump(path, height_cm)
    finally:
        os.remove(path)
