import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
import tempfile
import os

# --- Page Config ---
st.set_page_config(
    page_title="SmartDocAI | Analytics",
    page_icon="📈",
    layout="wide"
)

# --- Add Sticky Footer ---
def add_footer():
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            padding: 1rem;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            font-size: 0.9rem;
            text-align: center;
            border-top: 1px solid #ffd700;
            z-index: 9999;
        }
        </style>
        <div class="footer">
               SmartDocAI | 23127@iiitu.ac.in
        </div>
    """, unsafe_allow_html=True)

# --- UI ---
st.title("📈 SmartDocAI Analytics")
st.markdown("Upload an audio file to view waveform, duration, speech speed and more insights.")

# --- Upload Audio ---
audio_file = st.file_uploader("🎧 Upload audio file", type=["wav", "mp3", "m4a"])

if audio_file:
    # Save temp audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_audio_path = tmp_file.name

    # Load audio using librosa
    audio, sr = librosa.load(tmp_audio_path)

    # --- Basic Stats ---
    duration = librosa.get_duration(y=audio, sr=sr)
    word_estimate = int(duration * 2.5)  # rough estimate: 2.5 words per second

    col1, col2, col3 = st.columns(3)
    col1.metric("Duration", f"{duration:.2f} sec")
    col2.metric("Estimated Words", f"{word_estimate}")
    col3.metric("Sample Rate", f"{sr} Hz")

    # --- Waveform Plot ---
    st.subheader("🎵 Audio Waveform")
    fig, ax = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(audio, sr=sr, alpha=0.7)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Waveform")
    st.pyplot(fig)

    # --- Spectrogram ---
    st.subheader("Spectrogram")
    st.caption("Shows frequency over time")
    X = librosa.stft(audio)
    Xdb = librosa.amplitude_to_db(abs(X))
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz', ax=ax2)
    ax2.set_title("Spectrogram")
    fig2.colorbar(img, ax=ax2, format="%+2.0f dB")
    st.pyplot(fig2)

    # --- Cleanup ---
    os.remove(tmp_audio_path)
else:
    st.info("Please upload an audio file to generate analytics.")

# --- Add Spacer and Footer ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
add_footer()
