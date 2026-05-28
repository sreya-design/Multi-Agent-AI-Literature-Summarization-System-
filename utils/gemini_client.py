import os
import time
import google.generativeai as genai
from typing import Optional

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment variables.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

def call_gemini(prompt: str, retries: int = 3, delay: float = 2.0) -> Optional[str]:
    """Call Gemini with retry logic and rate-limit handling."""
    model = get_gemini_client()
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "rate" in err or "429" in err:
                wait = delay * (2 ** attempt)
                time.sleep(wait)
            elif attempt == retries - 1:
                raise RuntimeError(f"Gemini API error after {retries} attempts: {e}")
            else:
                time.sleep(delay)
    return None
