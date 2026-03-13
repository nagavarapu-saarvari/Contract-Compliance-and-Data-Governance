import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class DetectorGenerationAgent:

    def __init__(self):

        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )

        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    def generate_detectors(self, rules):

        system_prompt = """
You generate regex detectors for governance rule enforcement.

Output JSON:

{
 "detectors":[
  {
   "rule_id":"",
   "category":"",
   "regex":[]
  }
 ]
}
"""

        user_prompt = f"""
Generate regex detectors for these governance rules:

{json.dumps(rules, indent=2)}
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

        result = json.loads(response.choices[0].message.content)

        return result.get("detectors", [])