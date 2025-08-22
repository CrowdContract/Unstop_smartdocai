import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
from gtts import gTTS
import whisper
import tempfile
import base64
import numpy as np
import soundfile as sf
import av
import easyocr
import cv2
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

st.set_page_config(page_title="SmartDocAI | Features", page_icon="🧠", layout="centered")

@st.cache_resource
def load_model():
    return whisper.load_model("base")
model = load_model()

def set_background(image_path):
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
        margin-bottom: 2rem;
        background-color: rgba(0,0,0,0.5);
        border-radius: 12px;
    }}
    .title-box h1 {{
        color: #ffffff;
    }}
    .feature-bar {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 2rem;
        margin-bottom: 2rem;
        padding-left: 1rem;
        flex-wrap: wrap;
    }}
    .feature-box {{
        font-size: 1.2rem;
        background-color: #222;
        color: #fff;
        padding: 10px 20px;
        border-radius: 10px;
        text-align: center;
        width: fit-content;
    }}
    .main-box {{
        background-color: rgba(0, 0, 0, 0.4);
        padding: 2rem;
        border-radius: 15px;
        color: white;
    }}
    .transcript-box {{
        background-color: #222;
        color: #fff;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
    }}
    .footer {{
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.9rem;
        color: #ccc;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("assets/background.jpg")

st.markdown("""
    <div class="title-box">
        <h1>SmartDocAI Features</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="feature-bar">
        <div class="feature-box">✨ Choose a Feature</div>
    </div>
""", unsafe_allow_html=True)

option = st.radio("", ["🖼️ Image to Text", "🎤 Voice to Text", "📝 Text to Voice", "🔊 Speak"], horizontal=True, label_visibility="collapsed")

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

elif option == "🔊 Speak":
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    st.subheader("🎙️ Click below and speak. When you're done, transcription will appear.")

    class AudioProcessor(AudioProcessorBase):
        def __init__(self):
            self.frames = []

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().flatten()
            self.frames.append(audio)
            return frame

    ctx = webrtc_streamer(
        key="live-audio",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
        audio_processor_factory=AudioProcessor,
    )

    if ctx.audio_processor and st.button("🔝 Stop & Transcribe"):
        raw_audio = np.concatenate(ctx.audio_processor.frames, axis=0)
        if raw_audio.size == 0:
            st.error("⚠️ No audio recorded. Please try again.")
        else:
            audio_data = raw_audio.astype(np.int16).astype(np.float32) / 32768.0
            temp_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_path, audio_data, 16000, format='WAV')
            st.audio(temp_path)
            with st.spinner("Transcribing with Whisper..."):
                result = model.transcribe(temp_path)
            st.success("✅ Transcription Complete:")
            st.markdown(f'<div class="transcript-box">{result["text"]}</div>', unsafe_allow_html=True)
            st.download_button("📅 Download Transcript", result["text"], file_name="live_transcript.txt")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="footer">
        SmartDocAI | <a href="mailto:23127@iiitu.ac.in" style="color: #ffd700; text-decoration: none;">23127@iiitu.ac.in</a>
    </div>
""", unsafe_allow_html=True)
