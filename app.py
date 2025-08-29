import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="SmartDocAI", page_icon="🧠", layout="wide")

# --- Global Styling ---
def set_css():
    st.markdown("""
    <style>
        /* Global Styles */
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(to bottom right, #0A0A0A, #1E1E1E);
            color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .stApp {
            margin: 0;
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: #141414 !important;
            color: #f5f5f5;
            border: none;
            box-shadow: none;
            padding-top: 3rem;
        }

        /* Main Title */
        h1 {
            font-size: 3.2rem;
            font-weight: 700;
            color: #ffd700;
            text-align: center;
            margin-top: 2rem;
            margin-bottom: 1rem;
            text-shadow: 0 4px 12px rgba(0,0,0,0.6);
        }
        h2 {
            color: #ffd700;
            font-size: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        }

        /* Markdown Text */
        .stMarkdown {
            font-size: 1.1rem;
            line-height: 1.7;
            margin: 0 auto;
            text-align: center;
            max-width: 900px;
        }

        /* Card Layout */
        .feature-card {
            background: #1e1e1e;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: center;
        }
        .feature-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }

        /* Button Styling */
        .stButton button {
            background-color: #ffd700;
            color: black;
            padding: 12px 26px;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 30px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background-color: #f7e600;
            transform: scale(1.05);
            box-shadow: 0 6px 18px rgba(0,0,0,0.4);
        }

        /* Footer */
        footer {
            background-color: rgba(0,0,0,0.75);
            color: #f5f5f5;
            padding: 1rem;
            text-align: center;
            font-size: 0.95rem;
            font-weight: 500;
            border-radius: 10px 10px 0 0;
            margin-top: 3rem;
        }
        footer a {
            color: #ffd700;
            text-decoration: none;
        }
        footer a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Apply Global Styling ---
set_css()

# --- Sidebar Navigation ---
st.sidebar.title(" SmartDocAI")
page = st.sidebar.radio("Navigation", ("Home", "Features", "Analytics"), label_visibility="collapsed")

# --- Home Page ---
if page == "Home":
    st.title("Welcome to SmartDocAI")
    st.markdown("""
        SmartDocAI empowers accessibility through **AI-driven document insights**.  
        Upload resumes, extract meaning, and explore powerful features — all in one place.
    """)

    # Features Cards
    st.markdown("### 🚀 Key Features")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="feature-card"><h3>📄 Image → Text</h3><p>Extract text from images with OCR.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>🎤 Voice → Text</h3><p>Convert recorded speech into accurate transcripts.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>🔊 Text → Voice</h3><p>Generate natural voice from written text.</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="feature-card"><h3>🖥️ Live Recognition</h3><p>Real-time speech recognition for live inputs.</p></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### 🌟 Try It Out")
    st.button("Go to Features")

# --- Features Page ---
elif page == "Features":
    import pages.features

# --- Analytics Page ---
elif page == "Analytics":
    import pages.analytics

# --- Footer ---
st.markdown("""
    <footer>
        SmartDocAI © 2025 | Made with  | Contact: <a href="mailto:23127@iiitu.ac.in">23127@iiitu.ac.in</a>
    </footer>
""", unsafe_allow_html=True)
