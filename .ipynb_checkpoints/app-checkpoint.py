import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="SmartDocAI", page_icon="🧠", layout="wide")

# --- Global Styling ---
def set_css():
    st.markdown("""
    <style>
        /* Global Styles */
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(to bottom right, #0A0A0A, #111111);
            color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .stApp {
            margin: 0;
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: #1A1A1A;
            color: #f5f5f5;
            border: none;
            box-shadow: none;
            padding-top: 3rem;
        }
        .stSidebar .sidebar-content {
            padding: 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: #f5f5f5;
            text-align: center;
        }
        .stSidebar .stRadio button {
            background-color: #333;
            color: #f5f5f5;
            font-size: 1.1rem;
            padding: 12px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .stSidebar .stRadio button:hover {
            background-color: #ffd700;
            color: black;
        }

        /* Main Title */
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            color: #ffd700;
            text-align: center;
            margin-top: 4rem;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }

        /* Markdown Text */
        .stMarkdown {
            font-size: 1.2rem;
            line-height: 1.6;
            text-align: center;
            margin-top: 2rem;
        }
        .stMarkdown a {
            color: #ffd700;
            font-weight: bold;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: border-color 0.3s ease;
        }
        .stMarkdown a:hover {
            border-bottom: 2px solid #ffd700;
        }

        /* Button Styling */
        .stButton button {
            background-color: #ffd700;
            color: black;
            padding: 12px 30px;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 50px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            background-color: #f7e600;
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        }
        
        /* Footer */
        footer {
            background-color: rgba(0, 0, 0, 0.7);
            color: #f5f5f5;
            padding: 1.5rem;
            text-align: center;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 10px 10px 0 0;
            margin-top: 3rem;
            box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.3);
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

# --- Navigation Sidebar ---
st.sidebar.title("SmartDocAI")
page = st.sidebar.radio("Select a page", ("Home", "Features", "Analytics"), label_visibility="collapsed")

# --- Home Page ---
if page == "Home":
    st.title("Welcome to SmartDocAI")
    st.markdown("""
        SmartDocAI is designed to empower accessibility through AI-driven document understanding. 
        This application offers features like:
        - **Image to Text**
        - **Voice to Text**
        - **Text to Voice**
        - **Live Speech Recognition**
    """)
    st.markdown("[Go to Features](#features)", unsafe_allow_html=True)
    st.markdown("[Go to Analytics](#analytics)", unsafe_allow_html=True)

# --- Features Page ---
elif page == "Features":
    # Import and run features.py code here
    import pages.features

# --- Analytics Page ---
elif page == "Analytics":
    # Import and run analytics.py code here
    import pages.analytics

# --- Footer ---
st.markdown("""
    <footer>
        SmartDocAI | <a href="mailto:23127@iiitu.ac.in">23127@iiitu.ac.in</a>
    </footer>
""", unsafe_allow_html=True)
