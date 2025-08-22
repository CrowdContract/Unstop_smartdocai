import streamlit as st
import base64

# --- Page Config ---
st.set_page_config(
    page_title="SmartDocAI | Home",
    page_icon="🧠",
    layout="centered"
)

# --- Background Styling ---
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        .main-title {{
            font-size: 3rem;
            font-weight: bold;
            color: #fff;
            text-align: center;
            margin-top: 3rem;
            text-shadow: 1px 1px 5px rgba(0,0,0,0.6);
        }}
        .tagline {{
            font-size: 1.3rem;
            color: #ffd700;
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 2.5rem;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}
        .btn-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
        }}
        .custom-button {{
            background-color: transparent;
            color: #ffd700;
            border: 2px solid #ffd700;
            padding: 0.75rem 2.5rem;
            font-size: 1rem;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s ease-in-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        .custom-button:hover {{
            background-color: #ffd700;
            color: black;
            transform: scale(1.05);
        }}
        .image-row {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin: 3rem 0 2rem 0;
        }}
        .image-row img {{
            max-width: 250px;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.4);
            transition: transform 0.3s;
        }}
        .image-row img:hover {{
            transform: scale(1.05);
        }}
        .footer {{
            margin-top: auto;
            text-align: center;
            font-size: 1rem;
            color: #ffd700;
            font-weight: 600;
            font-family: 'Segoe UI', sans-serif;
            text-shadow: 1px 1px 2px #000;
            background: rgba(0, 0, 0, 0.3);
            padding: 0.5rem 1rem;
            border-top: 1px solid #ffd70033;
            border-radius: 8px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }}
        a {{
            color: #ffd700;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- Set background ---
set_background("assets/background.jpg")

# --- Main UI Content ---
st.markdown('<div class="main-title">Welcome to SmartDocAI</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Empowering Accessibility through AI-driven Document Understanding</div>', unsafe_allow_html=True)

# --- Centered Button with Golden Outline and Bold Text ---
st.markdown('''
    <div class="btn-container">
        <a href="/Features">
            <button class="custom-button"><b>Get Started</b></button>
        </a>
    </div>
''', unsafe_allow_html=True)

# --- Row of 3 Images (SLD Illustrations) ---
def show_image_row():
    images = ["assets/sld1.jpg", "assets/sld2.jpg", "assets/sld3.jpg"]
    links = [None, "/Features", "/Analytics"]
    encoded_imgs = []

    for img_path in images:
        with open(img_path, "rb") as img_file:
            encoded_imgs.append(base64.b64encode(img_file.read()).decode())

    html_imgs = ""
    for i, enc in enumerate(encoded_imgs):
        if links[i]:
            html_imgs += f'<a href="{links[i]}"><img src="data:image/jpg;base64,{enc}" alt="SLD Illustration {i+1}"/></a>'
        else:
            html_imgs += f'<img src="data:image/jpg;base64,{enc}" alt="SLD Illustration {i+1}"/>'

    st.markdown(f'''
        <div class="image-row">
            {html_imgs}
        </div>
    ''', unsafe_allow_html=True)

show_image_row()

# --- Sticky Footer ---
st.markdown("""
    <div class="footer">
        SmartDocAI | <a href="mailto:23111@iiitu.ac.in">23127@iiitu.ac.in</a>
    </div>
""", unsafe_allow_html=True)
