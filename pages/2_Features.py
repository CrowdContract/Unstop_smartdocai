import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
from gtts import gTTS
import whisper
import tempfile
import base64
import numpy as np
import soundfile as sf
import easyocr
import cv2
import requests

# ---------------- Config ----------------
BACKEND_URL = os.environ.get("SMARTDOCAI_BACKEND", "http://127.0.0.1:8000")

st.set_page_config(page_title="SmartDocAI | Features", page_icon="🧠", layout="wide")

@st.cache_resource(show_spinner=False)
def load_model():
    return whisper.load_model("base")
model = load_model()

# ---------------- Styling ----------------
def set_background(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Segoe UI', sans-serif;
        }}
        .title-box {{
            text-align: center;
            padding: 1rem;
            margin-bottom: 1.25rem;
            background-color: rgba(0,0,0,0.5);
            border-radius: 12px;
        }}
        .title-box h1 {{ color: #ffffff; margin: 0; }}
        .feature-bar {{
            display: flex; align-items: center; gap: .75rem; flex-wrap: wrap;
            margin-bottom: .75rem; padding-left: .25rem;
        }}
        .feature-box {{
            font-size: .95rem; background-color: #222; color: #fff;
            padding: 8px 14px; border-radius: 10px; width: fit-content;
        }}
        .main-box {{ background-color: rgba(0, 0, 0, 0.45); padding: 1rem; border-radius: 15px; color: white; }}
        .transcript-box {{ background-color: #222; color: #fff; padding: 1rem; border-radius: 10px; margin-top: 1rem; font-family: monospace; white-space: pre-wrap; }}
        .footer {{ text-align: center; margin-top: 3rem; padding: 1rem; font-size: 0.9rem; color: #ccc; }}
        .history-item {{ background:#111a; padding:.75rem; border-radius:10px; margin-bottom:.5rem; }}
        .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#333; margin-left:6px; font-size:0.8rem; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass

set_background("assets/background.jpg")

st.markdown('<div class="title-box"><h1>SmartDocAI Features</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="feature-bar"><div class="feature-box">✨ Choose a Feature</div></div>', unsafe_allow_html=True)

option = st.radio(
    "",
    ["🖼️ Image to Text", "🎤 Voice to Text", "📝 Text to Voice", "📄 Resume Insights"],
    horizontal=True,
    label_visibility="collapsed",
)

# ---------------- Image to Text ----------------
if option == "🖼️ Image to Text":
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.subheader("🖼️ Upload an image to extract text and convert to voice")

    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if image_file:
        st.image(image_file, caption="Uploaded Image", use_container_width=True)
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        image_np = cv2.imdecode(file_bytes, 1)

        with st.spinner("🔍 Extracting text..."):
            reader = easyocr.Reader(['en'], gpu=False)

            height, width, _ = image_np.shape
            mid = width // 2
            left_col = image_np[:, :mid]
            right_col = image_np[:, mid:]

            left_text = reader.readtext(left_col, paragraph=True)
            right_text = reader.readtext(right_col, paragraph=True)

            extracted_text = "\n\n".join([res[1] for res in left_text + right_text])

        if extracted_text.strip():
            st.success("✅ Extraction Complete:")
            st.markdown(f'<div class="transcript-box">{extracted_text}</div>', unsafe_allow_html=True)
            st.download_button("📅 Download Text", extracted_text, file_name="extracted_text.txt")

            st.markdown("---")
            st.subheader("🔊 Text to Voice from Image")
            with st.spinner("Generating voice..."):
                tts = gTTS(text=extracted_text, lang="en")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    tts.save(temp_audio.name)
                    audio_path = temp_audio.name
                st.success("✅ Voice Generated!")
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("📥 Download Audio", f.read(), file_name="image_text_audio.mp3")
        else:
            st.warning("⚠️ No text found in the image.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Voice to Text ----------------
elif option == "🎤 Voice to Text":
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.subheader("🎧 Upload an audio file to transcribe")

    audio_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])
    if audio_file:
        st.audio(audio_file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(audio_file.read())
            temp_path = temp_audio.name

        with st.spinner("Transcribing with Whisper..."):
            result = model.transcribe(temp_path)

        st.success("✅ Transcription Complete:")
        st.markdown(f'<div class="transcript-box">{result["text"]}</div>', unsafe_allow_html=True)
        st.download_button("📅 Download Transcript", result["text"], file_name="transcript.txt")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Text to Voice ----------------
elif option == "📝 Text to Voice":
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.subheader("💬 Enter text to convert into speech")

    user_input = st.text_area("Your text here...", height=150)
    if st.button("🔊 Convert and Play"):
        if user_input.strip():
            tts = gTTS(text=user_input, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                tts.save(temp_audio.name)
                audio_path = temp_audio.name
            st.success("✅ Conversion Successful!")
            st.audio(audio_path)
            with open(audio_path, "rb") as f:
                st.download_button("📅 Download Audio", f.read(), file_name="generated_audio.mp3")
        else:
            st.warning("⚠️ Please enter some text.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Resume Insights ----------------
elif option == "📄 Resume Insights":
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.subheader("📄 Upload Resume (PDF) → AI Summary + History")

    tabs = st.tabs(["Upload", "History"])

    # ---- Upload tab ----
    with tabs[0]:
        pdf_file = st.file_uploader("Upload a PDF resume", type=["pdf"])
        if pdf_file:
            if st.button("🚀 Analyze Resume", type="primary"):
                try:
                    with st.spinner("Uploading to backend and generating summary..."):
                        files = {"file": (pdf_file.name, pdf_file.read(), "application/pdf")}
                        resp = requests.post(f"{BACKEND_URL}/upload-resume", files=files, timeout=90)
                    if resp.status_code == 200:
                        data = resp.json()
                        if "error" in data:
                            st.error(f"Backend error: {data['error']}")
                        else:
                            st.success("✅ Summary ready!")
                            st.markdown("**Filename:** " + data.get("filename", ""))
                            st.markdown("**Uploaded at (UTC):** " + data.get("uploaded_at", ""))
                            st.markdown("**Used fallback:** " + str(data.get("used_fallback")))
                            st.markdown("### 🧠 Summary")
                            st.markdown(f'<div class="transcript-box">{data.get("summary","")}</div>', unsafe_allow_html=True)
                            if data.get("top_words"):
                                st.markdown("**Top words (fallback):** " + ", ".join(data["top_words"]))
                    else:
                        st.error(f"Backend error ({resp.status_code}): {resp.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

    # ---- History tab ----
    with tabs[1]:
        try:
            with st.spinner("Fetching history..."):
                hist_resp = requests.get(f"{BACKEND_URL}/insights?limit=50", timeout=30)
            if hist_resp.status_code == 200:
                payload = hist_resp.json()
                if isinstance(payload, dict) and "error" in payload:
                    st.error(payload["error"])
                else:
                    items = payload if isinstance(payload, list) else []
                    if not items:
                        st.info("No history yet. Upload a resume in the 'Upload' tab.")
                    else:
                        labels = [f"#{it['id']} • {it['filename']} • {it['uploaded_at']}" for it in items]
                        idx = st.selectbox("Select an entry", options=list(range(len(items))), format_func=lambda i: labels[i])
                        sel = items[idx]

                        st.markdown("---")
                        colA, colB = st.columns([2, 1])
                        with colA:
                            st.markdown(f"**Filename:** {sel['filename']}")
                            st.markdown(f"**Uploaded at (UTC):** {sel['uploaded_at']}")
                            st.markdown(f"**Used fallback:** {sel['used_fallback']}")
                        with colB:
                            if sel.get("top_words"):
                                st.markdown("**Top words:**")
                                st.write(", ".join(sel["top_words"]))

                        st.markdown("### 🧠 Summary")
                        st.markdown(f'<div class="transcript-box">{sel["summary"]}</div>', unsafe_allow_html=True)

                        with st.expander("Fetch again by ID"):
                            st.code(f"GET {BACKEND_URL}/insights?id={sel['id']}")
                            if st.button("↻ Refresh this item"):
                                one = requests.get(f"{BACKEND_URL}/insights?id={sel['id']}", timeout=30).json()
                                if isinstance(one, dict) and "error" in one:
                                    st.error(one["error"])
                                else:
                                    st.markdown(f'<div class="transcript-box">{one.get("summary","")}</div>', unsafe_allow_html=True)
            else:
                st.error(f"Backend error ({hist_resp.status_code}): {hist_resp.text}")
        except Exception as e:
            st.error(f"Could not load history: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("""
    <div class="footer">
        SmartDocAI | <a href="mailto:23127@iiitu.ac.in" style="color: #ffd700; text-decoration: none;">23127@iiitu.ac.in</a>
    </div>
""", unsafe_allow_html=True)
