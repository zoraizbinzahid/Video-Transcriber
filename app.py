import os
import json
import tempfile
import ffmpeg
import streamlit as st
from faster_whisper import WhisperModel

# --- Page Configuration ---
st.set_page_config(page_title="Video to Transcript", page_icon="🎬", layout="wide")

st.title("🎬 Video-to-Transcript Software")
st.caption("R&D Pipeline: Streamlit + FFmpeg + faster-whisper")

# --- Helper Functions ---

def extract_audio(video_path, audio_path):
    """Stage 2: FFmpeg pulls audio track from video"""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, ac=1, ar="16000", format="wav")
            .overwrite_output()
            .run(quiet=True)
        )
        return True
    except ffmpeg.Error as e:
        st.error(f"FFmpeg error: {e}")
        return False


def format_timestamp(seconds):
    """Formats seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    total_ms = int(round(float(seconds) * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    mins, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments):
    """Stage 4a: Builds SRT formatted string"""
    srt_output = []
    for idx, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        srt_output.append(f"{idx}\n{start} --> {end}\n{seg['text']}\n")
    return "\n".join(srt_output)


def generate_json(segments):
    """Stage 4b: Builds structured JSON data"""
    data = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"],
        }
        for seg in segments
    ]
    return json.dumps(data, indent=2)


@st.cache_resource
def load_whisper_model(model_size):
    # Uses int8 quantization as specified in the report
    return WhisperModel(model_size, device="cpu", compute_type="int8")


# --- Sidebar Model Settings ---
st.sidebar.header("Transcription Settings")
model_choice = st.sidebar.selectbox(
    "Whisper Model",
    ["tiny", "base", "small"],
    index=0,
    help="tiny = fastest; small = more accurate (slower, larger download)",
)

# --- Stage 1: Video Upload ---
uploaded_file = st.file_uploader(
    "Upload a Video File (.mp4, .mov, .mkv)",
    type=["mp4", "mov", "mkv"],
)

if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Process & Transcribe", type="primary"):
        with st.spinner("Processing video..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                video_path = os.path.join(temp_dir, uploaded_file.name)
                audio_path = os.path.join(temp_dir, "extracted_audio.wav")

                with open(video_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                st.info("Stage 1/3: Extracting audio with FFmpeg...")
                if not extract_audio(video_path, audio_path):
                    st.stop()

                st.info("Stage 2/3: Transcribing audio with faster-whisper...")
                model = load_whisper_model(model_choice)
                segments_generator, info = model.transcribe(audio_path, beam_size=5)
                segments = [
                    {"start": seg.start, "end": seg.end, "text": seg.text.strip()}
                    for seg in segments_generator
                ]

                full_text = " ".join(seg["text"] for seg in segments)

                st.info("Stage 3/3: Generating output formats (.srt, .txt, .json)...")
                st.session_state["result"] = {
                    "full_text": full_text,
                    "srt": generate_srt(segments),
                    "json": generate_json(segments),
                    "language": getattr(info, "language", None),
                }

        st.success("Transcription Complete!")

# Persist downloads across Streamlit reruns
if "result" in st.session_state:
    result = st.session_state["result"]
    st.subheader("Transcript Preview")
    if result.get("language"):
        st.caption(f"Detected language: {result['language']}")
    st.text_area("Full Text", value=result["full_text"], height=200)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="Download .SRT",
            data=result["srt"],
            file_name="transcript.srt",
            mime="text/plain",
        )
    with col2:
        st.download_button(
            label="Download .TXT",
            data=result["full_text"],
            file_name="transcript.txt",
            mime="text/plain",
        )
    with col3:
        st.download_button(
            label="Download .JSON",
            data=result["json"],
            file_name="transcript.json",
            mime="application/json",
        )
