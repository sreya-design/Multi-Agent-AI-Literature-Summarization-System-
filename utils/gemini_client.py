import os
import time
from typing import Optional


def call_gemini(prompt: str, retries: int = 3, delay: float = 2.0) -> Optional[str]:
    """
    Primary: Google Gemini API
    Fallback: OpenAI GPT-4o-mini
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not gemini_key and not openai_key:
        raise ValueError("No API key set. Add a Gemini or OpenAI key in the sidebar.")

    # ── Try Gemini first ──────────────────────────────────────────────────────
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            text = None
            try:
                text = response.text
            except Exception:
                if hasattr(response, "candidates") and response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "text") and part.text:
                            text = part.text
                            break
            if text and text.strip():
                return text.strip()
        except Exception as e:
            err = str(e).lower()
            # If quota exceeded, fall through to OpenAI
            if "429" in err or "quota" in err or "exhausted" in err:
                if not openai_key:
                    raise RuntimeError(
                        "Gemini quota exceeded and no OpenAI fallback key provided."
                    )
                # Fall through to OpenAI below
            else:
                raise RuntimeError(f"Gemini error: {e}")

    # ── Fallback: OpenAI ──────────────────────────────────────────────────────
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            for attempt in range(retries):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                    )
                    text = response.choices[0].message.content
                    if text and text.strip():
                        return text.strip()
                except Exception as e:
                    err = str(e).lower()
                    if "rate" in err or "429" in err:
                        time.sleep(delay * (2 ** attempt))
                    elif attempt == retries - 1:
                        raise RuntimeError(f"OpenAI fallback error: {e}")
                    else:
                        time.sleep(delay)
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

    return None
