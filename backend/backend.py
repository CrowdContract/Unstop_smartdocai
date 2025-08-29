from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import PyPDF2
import os

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
DB_PATH = "smartdocai.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        content TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ================================
#  API Endpoints
# ================================

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a PDF resume and save text into database."""
    try:
        text = ""
        pdf_reader = PyPDF2.PdfReader(file.file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        # Save into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO resumes (filename, content) VALUES (?, ?)",
                       (file.filename, text))
        conn.commit()
        conn.close()

        return {"message": "Resume uploaded successfully", "filename": file.filename}

    except Exception as e:
        return {"error": str(e)}


@app.get("/insights")
def get_insights():
    """Fetch all uploaded resumes from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, content FROM resumes")
    rows = cursor.fetchall()
    conn.close()

    return {"resumes": [{"id": r[0], "filename": r[1], "content": r[2]} for r in rows]}
