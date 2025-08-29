# --- Core imports ---
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import pdfplumber
from datetime import datetime
import json
import re
from collections import Counter

# --- Env + HTTP ---
from dotenv import load_dotenv
import requests

# Load environment variables from .env
# Expected keys (optional):
#   SARVAM_API_KEY=your_key
#   SARVAM_SUMMARY_URL=https://<your-sarvam-endpoint>
load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_SUMMARY_URL = os.getenv("SARVAM_SUMMARY_URL")  # leave empty to always use fallback

# ================================
#  FastAPI Setup
# ================================
app = FastAPI(title="SmartDocAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 🔒 tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
#  Database Setup
# ================================
DB_PATH = "smartdocai.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def init_db():
    """Initialize database with full schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            content TEXT,
            summary TEXT,
            top_words TEXT,
            uploaded_at TEXT,
            used_fallback INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

# ================================
#  Utils
# ================================
WORD_RE = re.compile(r"[A-Za-z]{4,}")  # only words with 4+ letters


def extract_top_words(text: str, n: int = 5):
    words = [w.lower() for w in WORD_RE.findall(text)]
    counts = Counter(words).most_common(n)
    return [w for w, _ in counts]


def summarize_with_sarvam(text: str) -> str | None:
    """
    Try Sarvam AI summarization if SARVAM_SUMMARY_URL and SARVAM_API_KEY are set.
    Expected JSON response to contain a 'summary' field.
    Returns None if unavailable or on error.
    """
    if not SARVAM_SUMMARY_URL or not SARVAM_API_KEY:
        return None

    payload = {"text": text[:4000]}  # keep payload small
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(SARVAM_SUMMARY_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            summary = data.get("summary")
            if summary and summary.strip():
                return summary.strip()
        # Non-200 or missing summary -> treat as failure
        return None
    except Exception:
        return None


# ================================
#  API Endpoints
# ================================
@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a PDF resume, extract text, summarize (Sarvam if available), save history."""
    try:
        # Save uploaded file to disk
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        file_bytes = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Extract text using pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

        # Try AI summarization via Sarvam
        summary = summarize_with_sarvam(text)

        # Fallback: Top 5 most frequent words
        used_fallback = summary is None
        if used_fallback:
            top_words = extract_top_words(text, n=5)
            summary = "Fallback insight — Top 5 frequent words: " + ", ".join(top_words)
        else:
            top_words = extract_top_words(text, n=5)

        # Persist to DB
        uploaded_at = datetime.utcnow().isoformat()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO resumes (filename, filepath, content, summary, top_words, uploaded_at, used_fallback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file.filename,
                file_path,
                text,
                summary,
                json.dumps(top_words),
                uploaded_at,
                int(used_fallback),
            ),
        )
        conn.commit()
        conn.close()

        return {
            "filename": file.filename,
            "uploaded_at": uploaded_at,
            "summary": summary,
            "top_words": top_words,
            "used_fallback": used_fallback,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insights")
def get_insights(limit: int = 20, id: int | None = None):
    """Fetch resume history or a specific resume by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        if id:
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (id,))
        else:
            cursor.execute("SELECT * FROM resumes ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()

        items = []
        for r in rows:
            items.append(
                {
                    "id": r[0],
                    "filename": r[1],
                    "filepath": r[2],
                    "content": r[3],
                    "summary": r[4],
                    "top_words": json.loads(r[5]) if r[5] else [],
                    "uploaded_at": r[6],
                    "used_fallback": bool(r[7]),
                }
            )

        return items if not id else (items[0] if items else {})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
