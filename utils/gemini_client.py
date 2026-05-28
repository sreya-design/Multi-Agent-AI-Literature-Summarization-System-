import os
import time
from typing import Optional


def call_gemini(prompt: str, retries: int = 3, delay: float = 2.0) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Updated model list — newest names first
    model_names = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
    ]

    errors = []
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
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

            errors.append(f"{model_name}: empty response")

        except Exception as e:
            errors.append(f"{model_name}: {str(e)}")
            time.sleep(1)
            continue

    raise RuntimeError(
        f"All Gemini models failed. Errors:\n" + "\n".join(errors)
    )
