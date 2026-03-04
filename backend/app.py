import os
import io
import json
import tempfile
import psycopg2

from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from psycopg2.errors import UniqueViolation

from rule_generation import generate_rules_from_pdf
from rule_check import analyze_single_file

load_dotenv()


# ==========================================================
# FASTAPI INIT
# ==========================================================

app = FastAPI(title="Governance Rule Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# ==========================================================
# FILE UPLOAD
# ==========================================================

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".py")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and .py files are supported"
        )

    file_bytes = await file.read()

    conn = get_connection()
    cursor = conn.cursor()

    # check duplicate filename
    cursor.execute(
        "SELECT id FROM documents WHERE filename = %s",
        (filename,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="A file with this name already exists"
        )
    else:
        cursor.execute(
        """
        INSERT INTO documents (filename, file_data)
        VALUES (%s, %s)
        RETURNING id;
        """,
        (filename, psycopg2.Binary(file_bytes))
        )
        document_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
    file_type = "pdf" if filename.endswith(".pdf") else "python"

    return {
        "type": file_type,
        "message": "File uploaded successfully",
        "document_id": document_id
    }

# ==========================================================
# LIST DOCUMENTS
# ==========================================================

@app.get("/documents")
def list_documents():

    conn = get_connection()

    with conn.cursor() as cursor:

        cursor.execute("""
        SELECT id, filename, uploaded_at
        FROM documents
        ORDER BY uploaded_at DESC
        """)

        rows = cursor.fetchall()

    conn.close()

    documents = []

    for r in rows:

        documents.append({
            "id": r[0],
            "filename": r[1],
            "uploaded_at": r[2]
        })

    return documents


# ==========================================================
# DOWNLOAD DOCUMENT
# ==========================================================

@app.get("/document/{doc_id}")
def get_document(doc_id: int):

    conn = get_connection()

    with conn.cursor() as cursor:

        cursor.execute(
            "SELECT filename, file_data FROM documents WHERE id=%s",
            (doc_id,)
        )

        row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    filename, file_data = row

    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ==========================================================
# RULE GENERATION
# ==========================================================

@app.post("/generate_rules/{doc_id}")
def generate_rules(doc_id: int):

    def stream():

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT filename, file_data FROM documents WHERE id=%s",
                (doc_id,)
            )
            row = cursor.fetchone()

        conn.close()

        if not row:
            yield "Document not found\n"
            return

        filename, file_data = row

        if not filename.endswith(".pdf"):
            yield "Rule generation only works for PDF files\n"
            return

        yield "Parsing PDF...\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:

            temp_pdf.write(file_data)
            temp_pdf_path = temp_pdf.name

        yield "Generating governance rules...\n"

        rules = generate_rules_from_pdf(temp_pdf_path, doc_id)

        os.remove(temp_pdf_path)

        yield json.dumps({
            "type": "rules",
            "rules": rules
        }) + "\n"

    return StreamingResponse(stream(), media_type="text/plain")


# ==========================================================
# COMPLIANCE CHECK
# ==========================================================

@app.post("/check_compliance/{doc_id}")
def check_compliance(doc_id: int):

    def stream():

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT filename, file_data FROM documents WHERE id=%s",
                (doc_id,)
            )
            row = cursor.fetchone()

        conn.close()

        if not row:
            yield "Document not found\n"
            return

        filename, file_data = row

        if not filename.endswith(".py"):
            yield "Compliance check only works for Python files\n"
            return

        yield "Preparing Python file...\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        metadata = {
            "patients": ["patient_id", "ssn", "dob"],
            "healthcare_providers": ["provider_id", "npi"]
        }

        try:

            yield "Running compliance scanner...\n"

            for message in analyze_single_file(temp_path, metadata):
                yield message

        finally:

            os.remove(temp_path)

    return StreamingResponse(stream(), media_type="text/plain")

# ==========================================================
# SERVE FRONTEND
# ==========================================================

frontend_path = Path("frontend/build")

if frontend_path.exists():

    app.mount(
        "/",
        StaticFiles(directory=frontend_path, html=True),
        name="frontend"
    )