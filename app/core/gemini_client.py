import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


def call_gemini(prompt: str, retries: int = 5) -> str:
    """
    Calls Groq API with retry logic for rate limits,
    connection errors, and server errors.
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            error_str = str(e).lower()

            # Rate limit
            if "429" in error_str or "rate" in error_str:
                wait = 30 * (attempt + 1)
                print(f"Rate limit. Waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue

            # Connection error — wait and retry
            if "connection" in error_str or "timeout" in error_str or "network" in error_str:
                wait = 10 * (attempt + 1)
                print(f"Connection error. Waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue

            # Server error
            if "503" in error_str or "502" in error_str or "unavailable" in error_str:
                wait = 15 * (attempt + 1)
                print(f"Server error. Waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue

            # Unknown error — raise immediately
            raise

    raise Exception(
        "API failed after all retries. Check your internet connection and try again."
    )


def call_gemini_json(prompt: str) -> dict:
    """
    Calls Groq and parses response as JSON.
    Strips markdown code fences if present.
    """
    raw = call_gemini(prompt)

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    return json.loads(cleaned)