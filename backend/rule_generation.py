import os
import json
import psycopg2
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_docling import DoclingLoader

load_dotenv()


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
# PDF PARSER
# ==========================================================

class ParsePDFTool:

    def execute(self, file_path: str) -> str:

        loader = DoclingLoader(file_path)
        documents = loader.load()

        return "".join(doc.page_content for doc in documents)


# ==========================================================
# POLICY COMPILER
# ==========================================================

class PolicyCompilationTool:

    def __init__(self, llm: AzureLLMService):
        self.llm = llm

    def execute(self, contract_text: str) -> List[Dict]:

        system_prompt = """
You are a senior enterprise governance expert.

Convert enforceable obligations into structured rules.

Return STRICT JSON only.
"""

        user_prompt = f"""
Return the rules in this format:

{{
"rules":[
{{
"rule_id":"",
"title":"",
"description":"",
"action_category":"",
"conditions":{{
"applies_to":"",
"data_type":"",
"context":"",
"exceptions":""
}},
"effect":"deny | allow"
}}
]
}}

Contract:
{contract_text}
"""

        result = self.llm.generate_json(system_prompt, user_prompt)

        if isinstance(result, dict) and "rules" in result:
            return result["rules"]

        if isinstance(result, list):
            return result

        raise ValueError("Invalid JSON structure from LLM")


# ==========================================================
# DATABASE REPOSITORY
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

    def get_rules_by_document(self, document_id: int) -> List[Dict]:

        with self.conn.cursor() as cursor:

            cursor.execute("""
            SELECT rule_json
            FROM rules
            WHERE document_id = %s
            ORDER BY id
            """, (document_id,))

            rows = cursor.fetchall()

        return [row[0] for row in rows]


    def store(self, rules: List[Dict], document_id: int):

        with self.conn.cursor() as cursor:

            for rule in rules:

                cursor.execute("""
                INSERT INTO rules (document_id, rule_id, rule_json)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_id, rule_id) DO NOTHING
                """,
                (
                    document_id,
                    rule.get("rule_id"),
                    json.dumps(rule)
                ))

        self.conn.commit()


    def close(self):
        self.conn.close()


# ==========================================================
# ORCHESTRATOR
# ==========================================================

class RuleGenerationAgent:

    def __init__(self):

        self.llm = AzureLLMService()
        self.parse_tool = ParsePDFTool()
        self.policy_tool = PolicyCompilationTool(self.llm)
        self.repository = RuleRepository()


    def process_contract(self, pdf_path: str, document_id: int):

        existing_rules = self.repository.get_rules_by_document(document_id)

        if existing_rules:
            self.repository.close()
            return existing_rules

        contract_text = self.parse_tool.execute(pdf_path)

        rules = self.policy_tool.execute(contract_text)

        self.repository.store(rules, document_id)

        self.repository.close()

        return rules


# ==========================================================
# PUBLIC FUNCTION
# ==========================================================

def generate_rules_from_pdf(pdf_path: str, document_id: int):

    agent = RuleGenerationAgent()

    return agent.process_contract(pdf_path, document_id)