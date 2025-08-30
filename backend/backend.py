from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import PyPDF2
import re
import os
import logging

# ================================
#  Logging
# ================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
#  FastAPI Setup
# ================================
app = FastAPI()

# Allow frontend (Streamlit) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
#  Database Setup
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smartdocai.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        content TEXT,
        summary TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ================================
#  Text Cleaning + Summarization
# ================================
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def summarize_resume(text: str) -> str:
    text = clean_text(text)

    edu_match = re.search(r"(B\.?\s*Tech.*?)(?:\d{4}|Present)", text, re.IGNORECASE)
    education = edu_match.group(1) if edu_match else "Education details not found"

    exp_match = re.search(r"(Internship|Hackathon|Project).*?(?:\d{4}|Present)", text, re.IGNORECASE)
    experience = exp_match.group(0) if exp_match else "Experience details not found"

    summary = f"Education: {education}. Experience: {experience}."
    if not summary.strip():
        summary = text[:500]

    return summary

# ================================
#  API Endpoints
# ================================
@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file.file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        text = clean_text(text)
        summary = summarize_resume(text)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO resumes (filename, content, summary) VALUES (?, ?, ?)",
            (file.filename, text, summary)
        )
        conn.commit()
        conn.close()

        logger.info(f"Inserted resume: {file.filename}")

        return {
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        return {"error": str(e)}

@app.get("/insights")
def get_insights():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, content, summary FROM resumes")
    rows = cursor.fetchall()
    conn.close()

    return {
        "resumes": [
            {"id": r[0], "filename": r[1], "content": r[2], "summary": r[3]}
            for r in rows
        ]
    }
