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

        Rules:
        - generate_rules → user wants governance rules from a contract
        - check_compliance → user wants to scan Python code for rule violations
        - unknown → anything else

        Return ONLY the intent label.
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

@app.post("/check_compliance")
async def check_compliance(request: Request):

    body = await request.json()

    contract_id = body.get("contract_id")
    python_id = body.get("python_id")

    if not contract_id or not python_id:
        raise HTTPException(
            status_code=400,
            detail="Both contract_id and python_id are required"
        )

    def stream():

        conn = get_connection()

        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT filename, file_data FROM documents WHERE id=%s",
                (python_id,)
            )

            row = cursor.fetchone()

        conn.close()

        if not row:
            yield "Python file not found\n"
            return

        filename, file_data = row

        if not filename.endswith(".py"):
            yield "Compliance check only works for Python files\n"
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
# PROMPT ROUTER (LLM + CONTRACT + PYTHON)
# ==========================================================

@app.post("/process_prompt")
async def process_prompt(request: Request):

    classifier = IntentClassifier()

    body = await request.json()

    prompt = body.get("prompt", "")
    contract_id = body.get("contract_id")
    python_id = body.get("python_id")

    intent = classifier.classify(prompt)

    if intent == "generate_rules":

        if not contract_id:
            return StreamingResponse(
                iter(["Please select a contract PDF file\n"]),
                media_type="text/plain"
            )

        return generate_rules(contract_id)


    if intent == "check_compliance":

        if not contract_id or not python_id:
            return StreamingResponse(
                iter(["Please select both a contract and Python file\n"]),
                media_type="text/plain"
            )

        def stream():

            conn = get_connection()

            with conn.cursor() as cursor:

                cursor.execute(
                    "SELECT file_data FROM documents WHERE id=%s",
                    (contract_id,)
                )
                contract_data = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT file_data FROM documents WHERE id=%s",
                    (python_id,)
                )
                python_data = cursor.fetchone()[0]

            conn.close()

            yield "Parsing contract...\n"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:

                temp_pdf.write(contract_data)
                contract_path = temp_pdf.name

            yield "Generating governance rules...\n"

            rules = generate_rules_from_pdf(contract_path, contract_id)

            os.remove(contract_path)

            yield "Preparing Python file...\n"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_py:

                temp_py.write(python_data)
                python_path = temp_py.name

            try:

                yield "Checking compliance using contract rules...\n"

                for message in analyze_single_file(python_path, contract_id):
                    yield message

            finally:

                os.remove(python_path)

        return StreamingResponse(stream(), media_type="text/plain")


    return StreamingResponse(
        iter(["Invalid request\n"]),
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
