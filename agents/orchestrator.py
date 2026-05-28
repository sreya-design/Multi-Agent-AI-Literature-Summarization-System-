import json
import re
from typing import List
from utils.gemini_client import call_gemini
from prompts.decompose import decompose_prompt

def decompose_topic(topic: str, num_questions: int = 4) -> List[str]:
    """
    Use Gemini to decompose a research topic into targeted sub-questions.
    Returns a list of sub-question strings.
    """
    prompt = decompose_prompt(topic, num_questions)
    response = call_gemini(prompt)

    if not response:
        raise ValueError("Gemini returned an empty response for topic decomposition.")

    # Extract JSON array from response
    try:
        # Try to find JSON array in response
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        if match:
            questions = json.loads(match.group())
        else:
            questions = json.loads(response.strip())

        if not isinstance(questions, list) or len(questions) == 0:
            raise ValueError("Invalid format")

        return [q.strip() for q in questions if isinstance(q, str) and q.strip()]

    except (json.JSONDecodeError, ValueError):
        # Fallback: split by newlines and clean up
        lines = [l.strip().lstrip("0123456789.-) ").strip() for l in response.split("\n") if l.strip()]
        questions = [l for l in lines if len(l) > 10][:num_questions]
        if not questions:
            raise ValueError(f"Could not parse sub-questions from Gemini response: {response[:300]}")
        return questions
