import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Force load the .env file from the backend directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("🚨 FATAL ERROR: GEMINI_API_KEY is missing from .env!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

def call_ai(prompt: str, schema: dict, temperature: float = 0.2):
    """Hits the Gemini API and guarantees JSON output."""
    try:
        # We use flash for lightning-fast hackathon responses
        model = genai.GenerativeModel('gemini-2.5-flash',
            generation_config={
                "temperature": temperature,
                "response_mime_type": "application/json", # Native JSON mode!
            }
        )
        
        # Inject the Pydantic schema into the system prompt
        full_prompt = f"""You are Sentinel, an autonomous AI security auditor. 
You must output ONLY valid JSON that strictly matches this schema:
{json.dumps(schema)}

USER PROMPT:
{prompt}"""
        
        response = model.generate_content(full_prompt)
        
        # Because we forced JSON MIME type, we can just load it directly
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": f"LLM parsing failed: {str(e)}"}