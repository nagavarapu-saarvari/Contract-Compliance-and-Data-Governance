import ast
import json
import os
import re
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
            self.lines[node.lineno-1:node.end_lineno]
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
# DETECTOR MATCH
# ----------------------------------------------------------

def detect_patterns(code, detectors):

    findings = []

    for d in detectors:

        for pattern in d.get("regex", []):

            try:

                if re.search(pattern, code, re.IGNORECASE):

                    findings.append({
                        "rule_id": d.get("rule_id"),
                        "category": d.get("category"),
                        "pattern": pattern
                    })

            except re.error:
                continue

    return findings


# ----------------------------------------------------------
# CONTEXT EXTRACTION
# ----------------------------------------------------------

def extract_context(code, pattern):

    lines = code.split("\n")

    for i, line in enumerate(lines):

        if re.search(pattern, line, re.IGNORECASE):

            start = max(0, i-2)
            end = min(len(lines), i+3)

            return "\n".join(lines[start:end])

    return code[:200]


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

    repo = RuleRepository()
    rules = repo.get_rules_by_document(document_id)
    repo.close()

    drepo = DetectorRepository()
    raw_detectors = drepo.get_detectors(document_id)

    detectors = []

    for row in raw_detectors:
        if isinstance(row, list):
            detectors.extend(row)
        else:
            detectors.append(row)

    drepo.close()

    suspicious = []

    for block in scanner.blocks:

        findings = detect_patterns(block["code"], detectors)

        if findings:

            

            suspicious.append({
                "function": block["name"],
    "code": block["code"],
    "findings": findings
            })

    if not suspicious:

        yield json.dumps({
             "type": "violations",
            "violations": [],
            "safe": True
        }) + "\n"

        return

    suspicious = suspicious[:5]

    relevant_rules = rules

    blocks_text = ""

    for b in suspicious:

        blocks_text += f"""
FUNCTION: {b['function']}

CODE:
{b['code']}

DETECTED PATTERNS:
{json.dumps(b['findings'], indent=2)}
"""

    system_prompt = """
You are an enterprise governance compliance engine.

You will receive:
1. Governance rules
2. Python code snippets
3. Detected suspicious patterns

For EACH function independently:

1. Check if the code violates any governance rule
2. If it does, return the rule_id and title from the provided rules
3. Multiple functions may violate multiple rules

IMPORTANT:
- Only use rule_ids from the provided rules
- Do not invent rules

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

    user_prompt = f"""
Rules:
{json.dumps(relevant_rules)}

Code snippets:
{blocks_text}
"""

    yield "Evaluating suspicious blocks with LLM...\n"
    print("LLM request starting...")

    llm = AzureLLMService()

    response = llm.client.chat.completions.create(
        model=llm.deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0,
        timeout=20
    )
    print("LLM response received")

    content = response.choices[0].message.content

    print("RAW LLM RESPONSE:")
    print(content)

    result = json.loads(content)

    violations = result.get("violations", [])

    yield json.dumps({
         "type": "violations",
        "violations": violations,
        "safe": len(violations) == 0
    }) + "\n"
    return