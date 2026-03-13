import os
import json
import psycopg2
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_docling import DoclingLoader

load_dotenv()


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


# ----------------------------------------------------------
# PDF PARSER
# ----------------------------------------------------------

class ParsePDFTool:

    def execute(self, file_path: str) -> str:

        loader = DoclingLoader(file_path)
        documents = loader.load()

        return "".join(doc.page_content for doc in documents)


# ----------------------------------------------------------
# POLICY COMPILER
# ----------------------------------------------------------

class PolicyCompilationTool:

    def __init__(self, llm: AzureLLMService):
        self.llm = llm

    def execute(self, contract_text: str) -> List[Dict]:

        system_prompt = """
You are a governance expert.

Convert contract obligations into enforceable governance rules.

Return JSON only.
"""

        user_prompt = f"""
Return rules in this format:

{{
 "rules":[
  {{
   "rule_id":"",
   "title":"",
   "description":"",
   "action_category":"",
   "conditions":{{}},
   "effect":"deny|allow"
  }}
 ]
}}

Contract:
{contract_text}
"""

        result = self.llm.generate_json(system_prompt, user_prompt)

        return result.get("rules", [])


# ----------------------------------------------------------
# DATABASE REPOSITORY
# ----------------------------------------------------------

class RuleRepository:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    def get_rules_by_document(self, document_id: int):

        with self.conn.cursor() as cursor:

            cursor.execute(
                "SELECT rule_json FROM rules WHERE document_id=%s",
                (document_id,)
            )

            rows = cursor.fetchall()

        return [r[0] for r in rows]

    def store(self, rules: List[Dict], document_id: int):

        with self.conn.cursor() as cursor:

            for rule in rules:

                cursor.execute(
                    """
                    INSERT INTO rules (document_id, rule_id, rule_json)
                    VALUES (%s,%s,%s)
                    ON CONFLICT (document_id,rule_id) DO NOTHING
                    """,
                    (
                        document_id,
                        rule.get("rule_id"),
                        json.dumps(rule)
                    )
                )

        self.conn.commit()

    def close(self):
        self.conn.close()


# ----------------------------------------------------------
# RULE GENERATION AGENT
# ----------------------------------------------------------

class RuleGenerationAgent:

    def __init__(self):

        self.llm = AzureLLMService()
        self.parser = ParsePDFTool()
        self.compiler = PolicyCompilationTool(self.llm)
        self.repo = RuleRepository()

    def process_contract(self, pdf_path, document_id):

        existing = self.repo.get_rules_by_document(document_id)

        if existing:
            self.repo.close()
            return existing

        text = self.parser.execute(pdf_path)

        rules = self.compiler.execute(text)

        self.repo.store(rules, document_id)

        self.repo.close()

        return rules


def generate_rules_from_pdf(pdf_path, document_id):

    agent = RuleGenerationAgent()

    return agent.process_contract(pdf_path, document_id)