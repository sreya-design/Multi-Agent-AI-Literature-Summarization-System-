import os
import time
from typing import Optional


def call_gemini(prompt: str, retries: int = 3, delay: float = 2.0) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model_names = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            for attempt in range(retries):
                try:
                    response = model.generate_content(prompt)
                    # Safe text extraction
                    text = None
                    try:
                        text = response.text
                    except Exception:
                        pass
                    if not text and hasattr(response, "candidates") and response.candidates:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, "text") and part.text:
                                text = part.text
                                break
                    if text and text.strip():
                        return text.strip()
                    # Check for blocked content
                    if hasattr(response, "prompt_feedback"):
                        raise RuntimeError(f"Content blocked: {response.prompt_feedback}")
                    raise RuntimeError("Empty text in response.")
                except RuntimeError:
                    raise
                except Exception as e:
                    err = str(e).lower()
                    if "quota" in err or "rate" in err or "429" in err:
                        time.sleep(delay * (2 ** attempt))
                    elif attempt == retries - 1:
                        raise
                    else:
                        time.sleep(delay)
        except Exception:
            continue  # try next model

    raise RuntimeError(
        "All Gemini models failed. Check your API key at https://aistudio.google.com"
    )
