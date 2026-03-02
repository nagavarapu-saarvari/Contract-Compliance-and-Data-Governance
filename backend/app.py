import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Import the rule generation and checking modules
from rule_generation import RuleGenerationAgent
from rule_check import  RuleRepository as CheckRuleRepository

app = FastAPI(title="Contract Compliance & Data Governance")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories if they don't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve React build files
react_build_dir = Path("frontend/build")
if react_build_dir.exists():
    app.mount("/static", StaticFiles(directory=str(react_build_dir / "static")), name="static")


# ==========================================================
# ROOT ENDPOINT
# ==========================================================

@app.get("/")
async def root():
    """Serve the React app"""
    index_path = Path("frontend/build/index.html")
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Contract Compliance System - React app not built yet. Run 'npm run build' in frontend folder."}


@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all routes"""
    index_path = Path("frontend/build/index.html")
    
    # Check if the requested path is a static file
    static_path = Path("frontend/build/static") / full_path
    if static_path.exists() and static_path.is_file():
        return FileResponse(static_path)
    
    # Otherwise serve index.html for React routing
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    
    return {"message": "Not Found"}



# ==========================================================
# PDF PROCESSING ENDPOINT
# ==========================================================

@app.post("/api/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and generate rules from it using rule_generation.py
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save the uploaded file
        temp_path = UPLOAD_DIR / file.filename
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # Process the PDF using rule generation
        agent = RuleGenerationAgent()
        rules = agent.process_contract(str(temp_path))

        # Clean up the temporary file
        if temp_path.exists():
            os.remove(temp_path)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "PDF processed successfully",
                "rules_count": len(rules),
                "rules": rules
            }
        )

    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            os.remove(temp_path)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error processing PDF: {str(e)}"
            }
        )


# ==========================================================
# PYTHON FILE COMPLIANCE CHECK ENDPOINT
# ==========================================================

@app.post("/api/check-compliance")
async def check_compliance(file: UploadFile = File(...)):
    """
    Upload a Python file and check it against stored rules.
    Only returns:
        - violation_found
        - safe
    """
    try:
        if not file.filename.lower().endswith(".py"):
            raise HTTPException(status_code=400, detail="Only Python files are supported")

        temp_path = UPLOAD_DIR / file.filename
        with open(temp_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        metadata = {
            "patients": ["patient_id", "ssn", "dob"],
            "healthcare_providers": ["provider_id", "npi"],
            "employees": ["employee_id", "ssn", "salary"],
            "customers": ["customer_id", "credit_card"],
            "users": ["user_id", "password", "email"]
        }

        import ast
        from rule_check import ComplianceScanner, AzureLLMService

        with open(temp_path, "r", encoding="utf-8") as f:
            code = f.read()

        tree = ast.parse(code)
        scanner = ComplianceScanner(code, metadata)
        scanner.visit(tree)

        violations_found = []

        # Only evaluate blocks if scanner flagged anything
        if scanner.blocks_for_review:
            rule_repo = CheckRuleRepository()
            rules = rule_repo.fetch_all_rules()
            llm = AzureLLMService()

            for block in scanner.blocks_for_review:
                result = llm.evaluate_block(block["code"], rules)
                violations = result.get("violations", [])

                if violations:
                    violations_found.append({
                        "block_scope": block["scope"],
                        "block_name": block["name"],
                        "violations": violations
                    })

        if temp_path.exists():
            os.remove(temp_path)

        # FINAL STATUS (Only 2 States)
        if violations_found:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "compliance_status": "violation_found",
                    "violations_count": len(violations_found),
                    "violations": violations_found
                }
            )
        else:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "compliance_status": "safe",
                    "violations_count": 0,
                    "violations": []
                }
            )

    except Exception as e:
        if 'temp_path' in locals() and temp_path.exists():
            os.remove(temp_path)

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error checking compliance: {str(e)}"
            }
        )

# ==========================================================
# RULES RETRIEVAL ENDPOINT
# ==========================================================

@app.get("/api/rules")
async def get_rules():
    """
    Retrieve all stored rules from the database
    """
    try:
        rule_repo = CheckRuleRepository()
        rules = rule_repo.fetch_all_rules()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "rules_count": len(rules),
                "rules": rules
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error retrieving rules: {str(e)}"
            }
        )


# ==========================================================
# HEALTH CHECK ENDPOINT
# ==========================================================

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "Contract Compliance System is running"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
