import json
import re
from typing import List
from utils.gemini_client import call_gemini
from prompts.decompose import decompose_prompt


def decompose_topic(topic: str, num_questions: int = 4) -> List[str]:
    prompt = decompose_prompt(topic, num_questions)
    response = call_gemini(prompt)  # raises on failure — no silent None

    # Strip markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", response.strip())
    text = re.sub(r"\s*```$", "", text).strip()

    # Try JSON array parse
    try:
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        parsed = json.loads(match.group() if match else text)
        if isinstance(parsed, list):
            result = [q.strip() for q in parsed if isinstance(q, str) and q.strip()]
            if result:
                return result
    except (json.JSONDecodeError, AttributeError):
        pass

    # Fallback: numbered/bulleted lines
    lines = [
        re.sub(r'^[\d\.\-\•\*\)>\s]+', '', l).strip()
        for l in text.splitlines() if l.strip()
    ]
    result = [l for l in lines if len(l) > 10][:num_questions]
    if result:
        return result

    raise ValueError(f"Could not parse sub-questions. Gemini said:\n{response[:300]}")
