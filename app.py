from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import PyPDF2
import datetime
import collections

app = FastAPI(title="SmartDocAI Backend")

# Allow frontend (Streamlit) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "smartdocai.db"

# ================================
# Database init + migration
# ================================
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
    # Add new columns if missing
    cols = [r[1] for r in cursor.execute("PRAGMA table_info(resumes);").fetchall()]
    if "summary" not in cols:
        cursor.execute("ALTER TABLE resumes ADD COLUMN summary TEXT")
    if "uploaded_at" not in cols:
        cursor.execute("ALTER TABLE resumes ADD COLUMN uploaded_at TEXT")
    if "used_fallback" not in cols:
        cursor.execute("ALTER TABLE resumes ADD COLUMN used_fallback TEXT")
    if "top_words" not in cols:
        cursor.execute("ALTER TABLE resumes ADD COLUMN top_words TEXT")
    conn.commit()
    conn.close()

init_db()

# ================================
# Fake summarizer (replace with Sarvam AI)
# ================================
def summarize_with_ai(text: str) -> str:
    sentences = text.split(".")
    return ". ".join(sentences[:3]).strip() if sentences else ""

# ================================
# API
# ================================
@app.get("/")
def root():
    return {"message": "SmartDocAI backend running", "endpoints": ["/upload-resume", "/insights"]}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Extract PDF text
        file.file.seek(0)
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = "\n".join([p.extract_text() or "" for p in pdf_reader.pages])

        uploaded_at = datetime.datetime.utcnow().isoformat()
        summary = summarize_with_ai(text)
        used_fallback = "False"
        top_words = []

        if not summary:
            used_fallback = "True"
            words = [w.lower() for w in text.split() if w.isalpha()]
            counter = collections.Counter(words)
            top_words = [w for w, _ in counter.most_common(5)]
            summary = "Fallback summary generated from top words."

        # Store in DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resumes (filename, content, summary, uploaded_at, used_fallback, top_words)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (file.filename, text, summary, uploaded_at, used_fallback, ",".join(top_words)))
        conn.commit()
        conn.close()

        return {
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "uploaded_at": uploaded_at,
            "summary": summary,
            "used_fallback": used_fallback,
            "top_words": top_words
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/insights")
def get_insights(id: int = None, limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if id:
        cursor.execute("SELECT id, filename, summary, uploaded_at, used_fallback, top_words FROM resumes WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {"error": "Resume not found"}
        return {
            "id": row[0],
            "filename": row[1],
            "summary": row[2],
            "uploaded_at": row[3],
            "used_fallback": row[4],
            "top_words": row[5].split(",") if row[5] else []
        }

    cursor.execute("SELECT id, filename, summary, uploaded_at, used_fallback, top_words FROM resumes ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "filename": r[1],
            "summary": r[2],
            "uploaded_at": r[3],
            "used_fallback": r[4],
            "top_words": r[5].split(",") if r[5] else []
        }
        for r in rows
    ]
