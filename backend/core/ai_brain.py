import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Force load the .env file from the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Initialize the client pointing to Groq's base URL
# (To use standard OpenAI, just remove the base_url and change the env var to OPENAI_API_KEY)
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def call_ai(prompt: str, schema: dict, temperature: float = 0.2):
    """Hits the AI API and guarantees JSON output."""
    try:
        full_prompt = f"""You are Sentinel, an autonomous AI security auditor.
You must output ONLY valid JSON that strictly matches this schema:
{json.dumps(schema)}

USER PROMPT:
{prompt}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Groq's fast Llama 3 model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a security auditing AI. Output valid JSON only."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=temperature
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ AI API Error: {error_msg}")
        
        # Safe fallback data to prevent FastApi from crashing
        schema_str = str(schema)
        if "auditor_findings" in schema_str: 
            return {
                "auditor_findings": [f"API Error: {error_msg[:50]}..."],
                "red_team_findings": ["Manual review required."],
                "severity_score": "INFO",
                "attack_surface_summary": "Scan bypassed."
            }
        elif "exploit_script" in schema_str: 
            return {"exploit_script": "# Exploit failed.", "execution_instructions": "N/A"}
        elif "patched_code" in schema_str:   
            return {"patched_code": "# Patch failed.", "security_principle": "N/A", "explanation": "N/A"}
        else: 
            return {"exploit_successful": False, "confidence_score": 0.0, "verdict_reasoning": "Bypassed."}