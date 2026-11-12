import json
import os
import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.8-flash"

SYSTEM_INSTRUCTIONS = """
You are SmartDesk AI, an assistant for an IT helpdesk.
Analyze the provided support ticket and return ONLY valid JSON matching the schema.
Be cautious: do not claim that a fix has been performed.
Do not request passwords, authentication codes, API keys, or other secrets.
Priority meanings:
- Critical: widespread outage, suspected security incident, or business-critical service unavailable.
- High: a user or team cannot perform an important work task.
- Medium: degraded functionality or a workaround exists.
- Low: minor issue, question, or cosmetic request.
Use concise, practical, safe troubleshooting steps. If the ticket suggests malware,
phishing, account compromise, or data loss, advise escalation to the appropriate IT/security team.
"""

def _get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")

def analyze_with_gemini(ticket_text: str) -> dict:
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    schema = {
        "type": "OBJECT",
        "properties": {
            "category": {"type": "STRING", "enum": ["Network", "Hardware", "Software", "Account & Access", "Security", "Other"]},
            "priority": {"type": "STRING", "enum": ["Low", "Medium", "High", "Critical"]},
            "sentiment": {"type": "STRING", "enum": ["Negative", "Neutral", "Positive"]},
            "summary": {"type": "STRING"},
            "troubleshooting_steps": {"type": "ARRAY", "items": {"type": "STRING"}},
            "response_draft": {"type": "STRING"}
        },
        "required": ["category", "priority", "sentiment", "summary", "troubleshooting_steps", "response_draft"]
    }

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=f"Analyze this support ticket:\n\n{ticket_text}",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.2,
            max_output_tokens=900,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    result = json.loads(response.text)
    return _validate_result(result)

def _validate_result(result: dict) -> dict:
    required = ["category", "priority", "sentiment", "summary", "troubleshooting_steps", "response_draft"]
    if not isinstance(result, dict) or any(key not in result for key in required):
        raise ValueError("AI response did not match the expected output structure.")
    if not isinstance(result["troubleshooting_steps"], list):
        raise ValueError("AI troubleshooting steps were not returned as a list.")
    return result
