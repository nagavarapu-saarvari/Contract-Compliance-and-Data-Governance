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
You generate REGEX DETECTORS that identify Python CODE BEHAVIOR
that could violate governance rules.

IMPORTANT RULES:

1. NEVER reuse words from the rule text.
2. Detect Python CODE OPERATIONS that implement the behavior.
3. Generate regex that matches Python syntax.

Examples:

Rule:
"Do not link datasets"

Correct detectors:
pd\\.merge\\(
\\.merge\\(
\\.join\\(
concat\\(
spark\\.sql\\(
JOIN\\s+

Rule:
"Do not export data"

Correct detectors:
to_csv\\(
to_excel\\(
to_json\\(
open\\(.*['\"]w
requests\\.post
boto3\\.client

Return JSON:

{
 "detectors":[
  {
   "rule_id":"",
   "category":"",
   "regex":[]
  }
 ]
}

Generate 10–20 regex patterns per rule covering
different Python implementations.
"""

        user_prompt = f"""
Generate regex detectors that match Python code patterns
for the following governance rules.

Rules:
{json.dumps(rules, indent=2)}

Remember:
Regex must match Python operations such as:

- dataframe merges
- dataframe joins
- file exports
- API calls
- SQL joins
- database queries
- filesystem writes

Rules:
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

        raw = response.choices[0].message.content

        print("RAW DETECTOR RESPONSE:")
        print(raw)

        result = json.loads(raw)

        detectors = result.get("detectors", [])

        print("Parsed detectors:", detectors)

        return detectors