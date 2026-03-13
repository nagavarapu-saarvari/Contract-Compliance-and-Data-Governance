import ast
import json
import re
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from detector_repository import DetectorRepository
from rule_generation import RuleRepository

load_dotenv()


# ----------------------------------------------------------
# AST SCANNER
# ----------------------------------------------------------

class ComplianceScanner(ast.NodeVisitor):

    def __init__(self, source):

        self.lines = source.split("\n")

        self.blocks = []

    def visit_FunctionDef(self, node):

        code = "\n".join(
            self.lines[node.lineno - 1:node.end_lineno]
        )

        self.blocks.append({
            "name": node.name,
            "code": code
        })

        self.generic_visit(node)


# ----------------------------------------------------------
# LLM SERVICE
# ----------------------------------------------------------

class AzureLLMService:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")


# ----------------------------------------------------------
# REGEX DETECTOR
# ----------------------------------------------------------

def detect_patterns(code, detectors):

    findings = []

    for d in detectors:

        patterns = d.get("regex", [])

        for pattern in patterns:

            try:

                compiled = re.compile(pattern, re.IGNORECASE)

                if compiled.search(code):

                    findings.append({
                        "rule_id": d.get("rule_id"),
                        "category": d.get("category"),
                        "pattern": pattern
                    })

            except re.error:
                continue

    return findings


# ----------------------------------------------------------
# MAIN ANALYSIS
# ----------------------------------------------------------

def analyze_single_file(path, document_id):

    yield "Scanning Python file...\n"

    with open(path) as f:
        code = f.read()

    tree = ast.parse(code)

    scanner = ComplianceScanner(code)

    scanner.visit(tree)

    print("Functions detected:", len(scanner.blocks))

    repo = RuleRepository()

    rules = repo.get_rules_by_document(document_id)

    repo.close()

    if not rules:
        yield "No governance rules found\n"
        return

    drepo = DetectorRepository()

    detectors = drepo.get_detectors(document_id)

    drepo.close()

    print("Detectors loaded:", len(detectors))

    if not detectors:
        yield "No detectors found for this contract\n"
        return

    suspicious = []

    for block in scanner.blocks:

        findings = detect_patterns(block["code"], detectors)

        if findings:

            suspicious.append({
                "function": block["name"],
                "code": block["code"],
                "findings": findings
            })

    print("Suspicious blocks:", len(suspicious))

    if not suspicious:

        yield json.dumps({
            "type": "violations",
            "violations": [],
            "safe": True
        }) + "\n"

        return

    # ----------------------------------------------------------
    # BATCH PROCESSING
    # ----------------------------------------------------------

    BATCH_SIZE = 5

    all_violations = []

    llm = AzureLLMService()

    system_prompt = """
You are an enterprise governance compliance engine.

You will receive:
1. Governance rules
2. Python code snippets
3. Detected suspicious patterns

Your task is to determine whether the code violates the rules.

Important guidelines:

1. Only report violations when the prohibited action is clearly present.
2. Do not speculate about possible misuse without evidence.
3. Internal mathematical transformations or analytics are NOT violations.
4. Internal logging or file writing is NOT a violation unless sensitive identifiers are exposed externally.
5. However, DO flag violations when code clearly performs actions such as:
   - exporting sensitive identifiers (SSN, patient_id, email, etc.)
   - transmitting data to external APIs or third-party services
   - joining or merging sensitive datasets
   - linking operational data with patient or identity tables
6. Use only the provided rule_ids.
7. A function may violate multiple rules.

Return JSON:

{
 "violations":[
  {
   "function":"",
   "rule_id":"",
   "title":"",
   "reason":""
  }
 ]
}
"""

    for i in range(0, len(suspicious), BATCH_SIZE):

        batch = suspicious[i:i+BATCH_SIZE]

        blocks_text = ""

        for b in batch:

            blocks_text += f"""
FUNCTION: {b['function']}

CODE:
{b['code'][:2000]}

DETECTED PATTERNS:
{json.dumps(b['findings'], indent=2)}
"""

        user_prompt = f"""
Rules:
{json.dumps(rules)}

Code snippets:
{blocks_text}
"""

        yield f"Evaluating batch {i//BATCH_SIZE + 1}...\n"

        response = llm.client.chat.completions.create(
            model=llm.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        raw = response.choices[0].message.content

        try:

            result = json.loads(raw)

            batch_violations = result.get("violations", [])

            all_violations.extend(batch_violations)

        except json.JSONDecodeError:

            print("Invalid JSON from LLM:", raw)

            continue

    yield json.dumps({
        "type": "violations",
        "violations": all_violations,
        "safe": len(all_violations) == 0
    }) + "\n"