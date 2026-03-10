import ast
import json
import os
import psycopg2
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


# ==========================================================
# RULE REPOSITORY
# ==========================================================

class RuleRepository:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    def fetch_rules_by_document(self, document_id):

        with self.conn.cursor() as cursor:

            cursor.execute(
                "SELECT rule_json FROM rules WHERE document_id=%s",
                (document_id,)
            )

            rows = cursor.fetchall()

        return [row[0] for row in rows]

    def close(self):
        self.conn.close()


# ==========================================================
# LLM SERVICE
# ==========================================================

class AzureLLMService:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")


    def evaluate_block(self, code_block, rules):

        system_prompt = """
You are an enterprise contract compliance engine.

You will receive:
1. Python code
2. Governance rules

Detect rule violations.

Return JSON:

{
"violations":[
{
"rule_id":"",
"title":"",
"reason":""
}
]
}
"""

        user_prompt = f"""
Rules:
{json.dumps(rules)}

Code:
{code_block}
"""

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        return json.loads(response.choices[0].message.content)


# ==========================================================
# AST SCANNER
# ==========================================================

class ComplianceScanner(ast.NodeVisitor):

    def __init__(self, source_code):

        self.source_code = source_code
        self.lines = source_code.split("\n")
        self.current_function = None
        self.blocks_for_review = []


    def visit_FunctionDef(self, node):

        self.current_function = node
        self.generic_visit(node)
        self.current_function = None


    def visit_Call(self, node):

        if self.current_function:

            code = "\n".join(
                self.lines[
                    self.current_function.lineno - 1:
                    self.current_function.end_lineno
                ]
            )

            if not any(b["code"] == code for b in self.blocks_for_review):

                self.blocks_for_review.append({
                    "scope": "function",
                    "name": self.current_function.name,
                    "code": code
                })

        self.generic_visit(node)


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def analyze_single_file(file_path: str, contract_id: int):

    yield "Scanning Python file...\n"

    try:

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        tree = ast.parse(code)

    except Exception as e:

        yield f"Failed to parse Python file: {str(e)}\n"

        yield json.dumps({
            "type": "violations",
            "violations": [],
            "safe": False
        }) + "\n"

        return


    scanner = ComplianceScanner(code)
    scanner.visit(tree)

    if not scanner.blocks_for_review:

        yield json.dumps({
            "type": "violations",
            "violations": [],
            "safe": True
        }) + "\n"

        return


    repo = RuleRepository()
    rules = repo.fetch_rules_by_document(contract_id)
    repo.close()

    llm = AzureLLMService()

    violations_list = []

    for block in scanner.blocks_for_review:

        try:

            result = llm.evaluate_block(block["code"], rules)

            violations = result.get("violations", [])

            for v in violations:

                violations_list.append({
                    "rule_id": v["rule_id"],
                    "title": v["title"],
                    "reason": v["reason"],
                    "scope": block["scope"],
                    "function": block["name"]
                })

        except Exception as e:

            violations_list.append({
                "rule_id": "SYSTEM",
                "title": "LLM evaluation error",
                "reason": str(e),
                "scope": block["scope"],
                "function": block["name"]
            })


    yield json.dumps({
        "type": "violations",
        "violations": violations_list,
        "safe": len(violations_list) == 0
    }) + "\n"