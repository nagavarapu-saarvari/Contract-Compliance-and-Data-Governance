import ast
import re
import json
import os
import psycopg2
from typing import Dict, List
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================

HTTP_LIBRARIES = ["requests", "httpx", "aiohttp"]
HTTP_METHODS = ["get", "post", "put", "delete", "patch"]

EXPORT_METHODS = [
    "to_csv",
    "to_excel",
    "to_json",
    "dump",
    "dumps"
]

SQL_PATTERN = re.compile(
    r"(SELECT|INSERT|UPDATE|DELETE).*?(FROM|INTO)\s+([\w\.]+)",
    re.IGNORECASE | re.DOTALL
)

JOIN_PATTERN = re.compile(
    r"\b(?:INNER|LEFT|RIGHT|FULL|CROSS|NATURAL)?\s*(?:OUTER)?\s*JOIN\s+([\w\.]+)",
    re.IGNORECASE
)

INTERNAL_PATHS = [
    "./",
    "/tmp/",
    "/var/",
    "/logs/",
    "logs/",
    "internal/"
]

# ==========================================================
# HELPER FUNCTION
# ==========================================================

def is_internal_path(path: str) -> bool:
    if not path:
        return False

    path = path.lower()
    return any(path.startswith(prefix) for prefix in INTERNAL_PATHS)

# ==========================================================
# DATABASE RULE REPOSITORY
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

    def fetch_all_rules(self) -> List[Dict]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT rule_json FROM rules;")
            rows = cursor.fetchall()
        return [row[0] for row in rows]

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

    def evaluate_block(self, code_block: str, rules: List[Dict]) -> Dict:

        system_prompt = """
        You are an enterprise contract compliance engine.

        You will receive:
        1. A Python code block.
        2. A list of governance rules.

        Determine whether the code violates any rule.
        If a rule has effect = "deny" and the code performs that action,
        mark it as a violation.

        Return STRICT JSON:

        {
        "violations": [
            {
                "rule_id": "",
                "title": "",
                "reason": ""
            }
        ]
        }
        """

        user_prompt = f"""
        Rules:
        {json.dumps(rules, indent=2)}

        Code Block:
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
# COMPLIANCE SCANNER
# ==========================================================

class ComplianceScanner(ast.NodeVisitor):

    def __init__(self, source_code: str, metadata: Dict):
        self.source_code = source_code
        self.lines = source_code.split("\n")

        self.metadata = {
            table.lower(): [col.lower() for col in cols]
            for table, cols in metadata.items()
        }

        self.current_function = None
        self.blocks_for_review = []
        self.module_scope_flagged = False

    def visit_FunctionDef(self, node):
        self.current_function = node
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):

        # ------------------------------
        # API Detection
        # ------------------------------
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            if method_name in HTTP_METHODS:
                
                self._register_review(node, "API call detected")

            # ------------------------------
            # Export Detection
            # ------------------------------
            if method_name in EXPORT_METHODS:

                export_path = None

                if node.args and isinstance(node.args[0], ast.Constant):
                    export_path = node.args[0].value

                for kw in node.keywords:
                    if isinstance(kw.value, ast.Constant):
                        export_path = kw.value.value

                if export_path and is_internal_path(export_path):
                    return

                self._register_review(
                    node,
                    f"Export detected: {export_path}"
                )

        # ------------------------------
        # open(..., "w") Detection
        # ------------------------------
        if isinstance(node.func, ast.Name) and node.func.id == "open":

            file_path = None
            mode = None

            if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                file_path = node.args[0].value

            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                mode = node.args[1].value

            if mode and "w" in mode:

                if file_path and is_internal_path(file_path):
                    return

                self._register_review(
                    node,
                    f"File write detected: {file_path}"
                )

        self.generic_visit(node)

    def visit_Constant(self, node):

        if isinstance(node.value, str):
            sql_text = node.value.lower()

            sql_matches = SQL_PATTERN.findall(sql_text)
            for match in sql_matches:
                table = match[2].split(".")[-1]
                if table in self.metadata:
                    self._register_review(
                        node,
                        f"Sensitive table '{table}' used"
                    )
                    return

            join_matches = JOIN_PATTERN.findall(sql_text)
            for join_table in join_matches:
                table = join_table.split(".")[-1]
                if table in self.metadata:
                    self._register_review(
                        node,
                        f"Sensitive JOIN '{table}' used"
                    )
                    return

        self.generic_visit(node)

    def _register_review(self, node, reason):

        if self.current_function:

            function_node = self.current_function

            function_code = "\n".join(
                self.lines[
                    function_node.lineno - 1:
                    function_node.end_lineno
                ]
            )

            if not any(f["code"] == function_code for f in self.blocks_for_review):
                self.blocks_for_review.append({
                    "scope": "function",
                    "name": function_node.name,
                    "reason": reason,
                    "code": function_code
                })

        else:

            if not self.module_scope_flagged:
                self.module_scope_flagged = True

                self.blocks_for_review.append({
                    "scope": "module",
                    "name": "<module_scope>",
                    "reason": reason,
                    "code": self.source_code
                })


# ==========================================================
# ORCHESTRATION
# ==========================================================

def analyze_single_file(file_path: str, metadata: Dict):

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    violation_count = 0
    tree = ast.parse(code)
    scanner = ComplianceScanner(code, metadata)
    scanner.visit(tree)

    if not scanner.blocks_for_review:
        print("No suspicious blocks detected.")
        return

    rule_repo = RuleRepository()
    rules = rule_repo.fetch_all_rules()

    llm = AzureLLMService()

    for block in scanner.blocks_for_review:
        
        result = llm.evaluate_block(block["code"], rules)
        violations = result.get("violations", [])

        if violations:
            violation_count += 1
            print(f"Scope: {block['scope']}")
            print(f"Name: {block['name']}")
            print(f"Initial Reason: {block['reason']}")
            print(f"\nCode:\n{block['code']}\n")
            print("Violations Detected:")
            for v in violations:
                print(f"- Rule {v['rule_id']}: {v['reason']}")
        else:
            continue

    if violation_count == 0:
        print("No Violations Detected")
        print("Safe to execute the file\n\n")

def analyze_multiple_files(files_list: List, metadata: Dict):
    print("\n\nCompliance Evaluation Results:\n")
    for file_name in files_list:
        print("-"*50)
        print(file_name)
        print("-"*50)
        analyze_single_file(file_name,metadata)
# ==========================================================
# RUN
# ==========================================================


metadata = {
    "patients": ["patient_id", "ssn", "dob"],
    "healthcare_providers": ["provider_id", "npi"]
}

file_list = ['test_scripts/test_script_breach.py','test_scripts/test_script_safe.py']
analyze_multiple_files(file_list ,metadata)