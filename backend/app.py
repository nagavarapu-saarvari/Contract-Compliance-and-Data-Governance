import os
import io
import json
import tempfile
import psycopg2

from openai import AzureOpenAI
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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
# LLM INTENT CLASSIFIER
# ==========================================================

class IntentClassifier:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def classify(self, prompt: str):

        system_prompt = """
You are an intent classification system.

Classify the user request into ONE of these intents:

generate_rules
check_compliance
unknown

Return only the label.
"""

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip().lower()


classifier = IntentClassifier()

# ==========================================================
# FILE UPLOAD
# ==========================================================

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):

    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".py")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and .py files supported"
        )

    file_bytes = await file.read()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM documents WHERE filename=%s",
        (filename,)
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="File already exists"
        )

    cursor.execute(
        """
        INSERT INTO documents (filename,file_data)
        VALUES (%s,%s)
        RETURNING id
        """,
        (filename, psycopg2.Binary(file_bytes))
    )

    document_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    file_type = "pdf" if filename.endswith(".pdf") else "python"

    return {
        "type": file_type,
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

    return [
        {"id": r[0], "filename": r[1], "uploaded_at": r[2]}
        for r in rows
    ]

# ==========================================================
# RULE GENERATION
# ==========================================================

@app.post("/generate_rules/{doc_id}")
def generate_rules(doc_id: int):

    def stream():

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT filename,file_data FROM documents WHERE id=%s",
                (doc_id,)
            )
            row = cursor.fetchone()

        conn.close()

        if not row:
            yield "Document not found\n"
            return

        filename, file_data = row

        if not filename.endswith(".pdf"):
            yield "Rule generation requires a PDF\n"
            return

        yield "Parsing contract...\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:

            temp_pdf.write(file_data)
            pdf_path = temp_pdf.name

        yield "Generating governance rules and detectors...\n"

        rules = generate_rules_from_pdf(pdf_path, doc_id)

        os.remove(pdf_path)

        yield json.dumps({
            "type": "rules",
            "rules": rules
        }) + "\n"

    return StreamingResponse(stream(), media_type="text/plain")

# ==========================================================
# COMPLIANCE CHECK
# ==========================================================

@app.post("/check_compliance")
async def check_compliance(request: Request):

    body = await request.json()

    contract_id = body.get("contract_id")
    python_id = body.get("python_id")

    if not contract_id or not python_id:
        raise HTTPException(
            status_code=400,
            detail="contract_id and python_id required"
        )

    def stream():

        conn = get_connection()

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT filename,file_data FROM documents WHERE id=%s",
                (python_id,)
            )

            row = cursor.fetchone()

        conn.close()

        if not row:
            yield "Python file not found\n"
            return

        filename, file_data = row

        if not filename.endswith(".py"):
            yield "Only Python files supported\n"
            return

        yield "Preparing Python file...\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:

            temp_file.write(file_data)
            temp_path = temp_file.name

        try:

            yield "Running compliance scanner...\n"

            for message in analyze_single_file(temp_path, contract_id):
                yield message

        finally:

            os.remove(temp_path)

    return StreamingResponse(stream(), media_type="text/plain")

# ==========================================================
# PROMPT ROUTER
# ==========================================================

@app.post("/process_prompt")
async def process_prompt(request: Request):

    body = await request.json()

    prompt = body.get("prompt", "")
    contract_id = body.get("contract_id")
    python_id = body.get("python_id")

    intent = classifier.classify(prompt)

    if intent == "generate_rules":

        if not contract_id:
            return StreamingResponse(
                iter(["Please select a contract\n"]),
                media_type="text/plain"
            )

        return generate_rules(contract_id)

    if intent == "check_compliance":

        if not contract_id or not python_id:
            return StreamingResponse(
                iter(["Select contract and python file\n"]),
                media_type="text/plain"
            )

        return await check_compliance(request)

    return StreamingResponse(
        iter(["Unknown request\n"]),
        media_type="text/plain"
    )

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