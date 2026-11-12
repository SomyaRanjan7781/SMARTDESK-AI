
import json
import logging
import os
import time

import streamlit as st
from google import genai
from google.genai import types


# Keep the model you are currently testing.
MODEL_NAME = "gemini-3.6-flash"

MAX_ATTEMPTS = 3
RETRYABLE_STATUS_CODES = (408, 429, 500, 502, 503, 504)

logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTIONS = """
You are SmartDesk AI, an assistant for an IT helpdesk.

Analyze the provided support ticket and return a structured JSON response.

Rules:
- Classify the issue accurately.
- Assign priority based on business impact and urgency.
- Identify the customer's sentiment.
- Write a concise issue summary.
- Provide practical and safe troubleshooting steps.
- Draft a professional response for the customer.
- Never claim that a fix has already been performed.
- Never ask for passwords, authentication codes, API keys,
  or other confidential information.
- If malware, phishing, account compromise, or data loss is suspected,
  recommend escalation to the appropriate IT/security team.

Priority meanings:
- Critical: Widespread outage, suspected security incident,
  or business-critical service unavailable.
- High: A user or team cannot perform an important work task.
- Medium: Degraded functionality or a workaround exists.
- Low: Minor issue, question, or cosmetic request.
"""


RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {
            "type": "STRING",
            "enum": [
                "Network",
                "Hardware",
                "Software",
                "Account & Access",
                "Security",
                "Other"
            ]
        },
        "priority": {
            "type": "STRING",
            "enum": [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        },
        "sentiment": {
            "type": "STRING",
            "enum": [
                "Negative",
                "Neutral",
                "Positive"
            ]
        },
        "summary": {
            "type": "STRING"
        },
        "troubleshooting_steps": {
            "type": "ARRAY",
            "items": {
                "type": "STRING"
            }
        },
        "response_draft": {
            "type": "STRING"
        }
    },
    "required": [
        "category",
        "priority",
        "sentiment",
        "summary",
        "troubleshooting_steps",
        "response_draft"
    ]
}


def _get_api_key():
    """Read the Gemini API key from Streamlit Secrets or environment."""

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.getenv("GEMINI_API_KEY", "")

    return key.strip() if key else ""


def _extract_error_code(error):
    """Try to extract an HTTP status code from an SDK exception."""

    code = getattr(error, "code", None)

    if code is None:
        code = getattr(error, "status_code", None)

    try:
        return int(code)
    except (TypeError, ValueError):
        return None


def _is_retryable_error(error):
    """Identify temporary API errors that may succeed on retry."""

    code = _extract_error_code(error)

    if code in RETRYABLE_STATUS_CODES:
        return True

    message = str(error).lower()

    retryable_terms = [
        "timeout",
        "timed out",
        "temporarily unavailable",
        "resource exhausted",
        "rate limit",
        "too many requests",
        "internal server error",
        "service unavailable",
        "connection reset"
    ]

    return any(term in message for term in retryable_terms)


def _validate_result(result):
    """Validate and normalize Gemini's structured response."""

    if hasattr(result, "model_dump"):
        result = result.model_dump()

    if not isinstance(result, dict):
        raise ValueError("Gemini response is not a valid JSON object.")

    required_fields = [
        "category",
        "priority",
        "sentiment",
        "summary",
        "troubleshooting_steps",
        "response_draft"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in result
    ]

    if missing_fields:
        raise ValueError(
            "Gemini response is missing fields: "
            + ", ".join(missing_fields)
        )

    allowed_categories = {
        "Network",
        "Hardware",
        "Software",
        "Account & Access",
        "Security",
        "Other"
    }

    allowed_priorities = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    allowed_sentiments = {
        "Negative",
        "Neutral",
        "Positive"
    }

    category = str(result["category"]).strip()
    priority = str(result["priority"]).strip().title()
    sentiment = str(result["sentiment"]).strip().title()

    # Support older records or model responses using "Access".
    if category == "Access":
        category = "Account & Access"

    if category not in allowed_categories:
        category = "Other"

    if priority not in allowed_priorities:
        raise ValueError("Gemini returned an invalid priority.")

    if sentiment not in allowed_sentiments:
        raise ValueError("Gemini returned an invalid sentiment.")

    summary = result["summary"]
    response_draft = result["response_draft"]
    steps = result["troubleshooting_steps"]

    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("Gemini returned an empty summary.")

    if not isinstance(response_draft, str) or not response_draft.strip():
        raise ValueError("Gemini returned an empty response draft.")

    if not isinstance(steps, list):
        raise ValueError("Troubleshooting steps must be a list.")

    steps = [
        str(step).strip()
        for step in steps
        if str(step).strip()
    ]

    if not steps:
        raise ValueError("Gemini returned no troubleshooting steps.")

    return {
        "category": category,
        "priority": priority,
        "sentiment": sentiment,
        "summary": summary.strip(),
        "troubleshooting_steps": steps,
        "response_draft": response_draft.strip()
    }


def _parse_response(response):
    """
    Prefer the SDK's parsed structured response.
    Use JSON text parsing only if parsed data is unavailable.
    """

    parsed = getattr(response, "parsed", None)

    if parsed is not None:
        return _validate_result(parsed)

    response_text = getattr(response, "text", None)

    if not response_text:
        raise ValueError(
            "Gemini returned an empty response. "
            "The response may have been blocked or truncated."
        )

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned incomplete or invalid JSON. "
            f"JSON error: {error}"
        ) from error

    return _validate_result(result)


def analyze_with_gemini(ticket_text: str) -> dict:
    """Analyze an IT support ticket using Gemini."""

    if not isinstance(ticket_text, str) or not ticket_text.strip():
        raise ValueError("Ticket description cannot be empty.")

    api_key = _get_api_key()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured in Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=(
                    "Analyze the following IT support ticket. "
                    "Return all required fields using the supplied schema.\n\n"
                    f"SUPPORT TICKET:\n{ticket_text.strip()}"
                ),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS,
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.2,
                    max_output_tokens=2048
                )
            )

            result = _parse_response(response)

            logger.info(
                "Gemini successfully analyzed a support ticket."
            )

            return result

        except Exception as error:
            last_error = error

            logger.exception(
                "Gemini analysis failed on attempt %s of %s.",
                attempt,
                MAX_ATTEMPTS
            )

            if attempt < MAX_ATTEMPTS and _is_retryable_error(error):
                time.sleep(attempt * 2)
                continue

            break

    raise RuntimeError(
        f"Gemini analysis failed after {attempt} attempt(s): "
        f"{type(last_error).__name__}: {last_error}"
    ) from last_error
