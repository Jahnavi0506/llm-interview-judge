import os
import json
import time
from groq import Groq
from app.config import MODEL_NAME, MAX_RETRIES, RETRY_WAIT_SECONDS
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_api_key() -> str:
    """
    Gets GROQ API key from either:
    1. Streamlit Cloud secrets (when deployed)
    2. Local .env file (when running locally)
    """
    # Try Streamlit secrets first (cloud deployment)
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass

    # Fall back to environment variable (local development)
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key

    raise ValueError(
        "GROQ_API_KEY not found. "
        "Set it in .env for local dev or Streamlit secrets for cloud."
    )


# Initialize client
client = Groq(api_key=get_api_key())
MODEL = MODEL_NAME


def call_gemini(prompt: str, retries: int = MAX_RETRIES) -> str:
    logger.info(f"API call started | model={MODEL} | prompt_length={len(prompt)}")

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            result = response.choices[0].message.content
            logger.info(f"API call success | attempt={attempt+1} | response_length={len(result)}")
            return result

        except Exception as e:
            error_str = str(e).lower()

            if "429" in error_str or "rate" in error_str:
                wait = RETRY_WAIT_SECONDS * (attempt + 1)
                logger.warning(f"Rate limit hit | attempt={attempt+1} | waiting={wait}s")
                time.sleep(wait)
                continue

            if "connection" in error_str or "timeout" in error_str:
                wait = 10 * (attempt + 1)
                logger.warning(f"Connection error | attempt={attempt+1} | waiting={wait}s")
                time.sleep(wait)
                continue

            if "503" in error_str or "502" in error_str or "unavailable" in error_str:
                wait = 15 * (attempt + 1)
                logger.warning(f"Server error | attempt={attempt+1} | waiting={wait}s")
                time.sleep(wait)
                continue

            logger.error(f"Unhandled API error | {str(e)}", exc_info=True)
            raise

    logger.error("All retries exhausted")
    raise Exception("API failed after all retries. Please wait and try again.")


def call_gemini_json(prompt: str) -> dict:
    raw = call_gemini(prompt)

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        result = json.loads(cleaned)
        logger.info("JSON parsing successful")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed | error={str(e)} | raw={raw[:200]}")
        raise