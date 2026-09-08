# Video-to-Transcript

Upload a video → extract audio (FFmpeg) → transcribe (faster-whisper) → download `.srt` / `.txt` / `.json`.

## Run on your computer

### 1. Prerequisites

- **Python 3.10+** (3.11 recommended)
- **FFmpeg** on your PATH

  Check: `ffmpeg -version`

  If missing on Windows (winget):

  ```powershell
  winget install Gyan.FFmpeg.Essentials
  ```

  Then **open a new terminal** so PATH updates apply.

### 2. Setup

```powershell
cd d:\Work\video-transcriber
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Launch the app

```powershell
streamlit run app.py
```

Browser opens at `http://localhost:8501`.

**First run note:** the Whisper model downloads from Hugging Face once (tiny ≈ 75 MB). Needs internet the first time.

### 4. Use it

1. Pick a model in the sidebar (`tiny` = fastest, `small` = more accurate)
2. Upload `.mp4` / `.mov` / `.mkv`
3. Click **Process & Transcribe**
4. Download `.srt`, `.txt`, or `.json`

## Deploy on Render (Docker)

This repo includes a `Dockerfile` with FFmpeg + Streamlit.

- Web service from Docker
- Start command is already in the Dockerfile (`streamlit run …`)
- Expose port **8501**
- Free tier CPU is fine for short clips with the `tiny` model; longer videos or `small` may need more RAM/time

## What’s included / not yet

| Feature | Status |
|--------|--------|
| File upload → transcript | Done |
| `.srt` / `.txt` / `.json` | Done |
| Model size dropdown | Done (`tiny` / `base` / `small`) |
| YouTube / Google Drive links | Not built (easy later with `yt-dlp`) |

## Project layout

```
app.py             # Streamlit UI + FFmpeg + faster-whisper pipeline
requirements.txt   # Python dependencies
Dockerfile         # Render / container deploy
README.md          # This guide
```
