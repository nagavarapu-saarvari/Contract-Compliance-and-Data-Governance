import os
import json
import psycopg2
import contextlib
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_docling import DoclingLoader

load_dotenv()

# ==========================================================
# ---------------- LLM SERVICE -----------------------------
# ==========================================================

class AzureLLMService:

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict:

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
# ---------------- PDF PARSER TOOL -------------------------
# ==========================================================

class ParsePDFTool:

    def execute(self, file_path: str) -> str:
        print("Parsing PDF...")

        loader = DoclingLoader(file_path)

        documents = loader.load()

        return "".join(doc.page_content for doc in documents)

# ==========================================================
# ---------------- POLICY COMPILATION TOOL -----------------
# ==========================================================

class PolicyCompilationTool:

    def __init__(self, llm: AzureLLMService):
        self.llm = llm

    def execute(self, contract_text: str) -> List[Dict]:

        print("Compiling contract into enforceable policies...")

        system_prompt = """
            You are a senior enterprise governance and compliance expert.
            Convert enforceable obligations into structured rules.
            Output STRICT JSON only.
            """

        user_prompt = f"""
            Return the rules in this format:

            {{
            "rules": [
                {{
                    "rule_id": "R1",
                    "title": "",
                    "description": "",
                    "action_category": "",
                    "conditions": {{
                        "applies_to": "",
                        "data_type": "",
                        "context": "",
                        "exceptions": ""
                    }},
                    "effect": "deny | allow"
                }}
                ]
            }}

            Contract:
            {contract_text}
            """

        result = self.llm.generate_json(system_prompt, user_prompt)

    # ------------------------------
    # SAFE NORMALIZATION LAYER
    # ------------------------------

        if isinstance(result, dict):

        # Case 1: Proper wrapped format
            if "rules" in result and isinstance(result["rules"], list):
                return result["rules"]

        # Case 2: Model returned dict of numeric keys
            if all(isinstance(v, dict) for v in result.values()):
                return list(result.values())

        if isinstance(result, list):
            return result

        raise ValueError("Policy compilation failed: Invalid JSON structure.")


# ==========================================================
# ---------------- DATABASE REPOSITORY ---------------------
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
        self._initialize()

    def _initialize(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id SERIAL PRIMARY KEY,
                    rule_id TEXT UNIQUE,
                    rule_json JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()

    def store(self, rules: List[Dict]) -> int:

        inserted_rows = 0

        with self.conn.cursor() as cursor:
            for rule in rules:
                rule_id = rule.get("rule_id")

                if not rule_id:
                    print("Skipping rule with missing rule_id.")
                    continue

                # Check if rule already exists
                cursor.execute(
                    "SELECT 1 FROM rules WHERE rule_id = %s;",
                    (rule_id,)
                )

                if cursor.fetchone():
                    print(f"Rule {rule_id} already exists. Skipping.")
                    continue

                # Insert rule
                cursor.execute("""
                    INSERT INTO rules (rule_id, rule_json)
                    VALUES (%s, %s);
                """, (rule_id, json.dumps(rule)))

                print(f"Rule {rule_id} inserted.")
                inserted_rows += 1

            self.conn.commit()

        return inserted_rows


# ==========================================================
# ---------------- AGENT ORCHESTRATOR ----------------------
# ==========================================================

class RuleGenerationAgent:

    def __init__(self):
        self.llm = AzureLLMService()
        self.parse_tool = ParsePDFTool()
        self.policy_tool = PolicyCompilationTool(self.llm)
        self.repository = RuleRepository()

    def process_contract(self, pdf_path: str):

        contract_text = self.parse_tool.execute(pdf_path)
        rules = self.policy_tool.execute(contract_text)

        print("\nGenerated Enterprise Rules:\n")
        print(json.dumps(rules, indent=2))

        inserted_rows = self.repository.store(rules)

        print("\nDatabase Summary:")

        if inserted_rows == 0:
            print("No new rules were inserted.")
        else:
            print(f"Number of rows inserted: {inserted_rows}")

        return rules


# ==========================================================
# ---------------- PUBLIC FUNCTION -------------------------
# ==========================================================

def generate_rules_from_pdf(pdf_path: str):
    agent = RuleGenerationAgent()
    return agent.process_contract(pdf_path)

if __name__ == "__main__":
    generate_rules_from_pdf("contract.pdf")