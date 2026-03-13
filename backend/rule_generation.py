import os
import json
import psycopg2
from dotenv import load_dotenv
from openai import AzureOpenAI
from langchain_docling import DoclingLoader

from detector_generation import DetectorGenerationAgent
from detector_repository import DetectorRepository

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

    def generate_json(self, system_prompt, user_prompt):

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        raw = response.choices[0].message.content

        print("LLM RAW RULE RESPONSE:")
        print(raw)

        return json.loads(raw)


# ----------------------------------------------------------
# PDF PARSER
# ----------------------------------------------------------

class ParsePDFTool:

    def execute(self, file_path):

        loader = DoclingLoader(file_path)

        docs = loader.load()

        text = "\n".join(doc.page_content for doc in docs)

        return text


# ----------------------------------------------------------
# POLICY COMPILER
# ----------------------------------------------------------

class PolicyCompilationTool:

    def __init__(self, llm):

        self.llm = llm

    def execute(self, contract_text):

        system_prompt = """
You are a governance expert.

Convert contract obligations into enforceable governance rules
that can be validated against source code.

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
# RULE DATABASE
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

    def get_rules_by_document(self, document_id):

        with self.conn.cursor() as cursor:

            cursor.execute(
                "SELECT rule_json FROM rules WHERE document_id=%s",
                (document_id,)
            )

            rows = cursor.fetchall()

        return [r[0] for r in rows]

    def store(self, rules, document_id):

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

        # --------------------------------------------
        # Check existing rules
        # --------------------------------------------

        existing_rules = self.repo.get_rules_by_document(document_id)

        if existing_rules:

            print("Rules already exist for this contract.")

            drepo = DetectorRepository()

            detectors = drepo.get_detectors(document_id)

            if detectors:
                print("Detectors already exist:", len(detectors))

                drepo.close()
                self.repo.close()

                return existing_rules

            print("Rules exist but detectors missing. Generating detectors...")

            detector_agent = DetectorGenerationAgent()

            detectors = detector_agent.generate_detectors(existing_rules)

            print("Generated detectors:", detectors)

            if detectors:

                drepo.store_detectors(document_id, detectors)

                print("Detectors stored:", len(detectors))

            else:

                print("No detectors generated!")

            drepo.close()
            self.repo.close()

            return existing_rules


        # --------------------------------------------
        # No rules exist → generate rules
        # --------------------------------------------

        print("Parsing contract...")

        contract_text = self.parser.execute(pdf_path)

        print("Generating governance rules...")

        rules = self.compiler.execute(contract_text)

        print("Generated rules:", rules)

        if not rules:

            print("No rules generated!")

            self.repo.close()

            return []


        # --------------------------------------------
        # Store rules
        # --------------------------------------------

        self.repo.store(rules, document_id)

        print("Rules stored:", len(rules))


        # --------------------------------------------
        # Generate detectors
        # --------------------------------------------

        print("Generating regex detectors...")

        detector_agent = DetectorGenerationAgent()

        detectors = detector_agent.generate_detectors(rules)

        print("Generated detectors:", detectors)


        # --------------------------------------------
        # Store detectors
        # --------------------------------------------

        drepo = DetectorRepository()

        if detectors:

            drepo.store_detectors(document_id, detectors)

            print("Detectors stored:", len(detectors))

        else:

            print("No detectors generated!")


        drepo.close()

        self.repo.close()

        return rules


# ----------------------------------------------------------
# MAIN ENTRY FUNCTION
# ----------------------------------------------------------

def generate_rules_from_pdf(pdf_path, document_id):

    agent = RuleGenerationAgent()

    return agent.process_contract(pdf_path, document_id)