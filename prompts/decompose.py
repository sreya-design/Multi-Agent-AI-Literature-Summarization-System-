def decompose_prompt(topic: str, num_questions: int = 4) -> str:
    return f"""You are a research strategist helping a scientist conduct a thorough literature review.

Given the research topic: "{topic}"

Generate exactly {num_questions} targeted sub-questions that together provide comprehensive coverage of this topic.
Each sub-question should:
- Focus on a distinct aspect (e.g., methods, applications, limitations, comparisons, recent advances)
- Be specific enough to retrieve focused ArXiv papers
- Be phrased as a short search-friendly query (3–8 words)

Respond ONLY with a JSON array of strings. No explanation, no markdown, no extra text.
Example format: ["question one", "question two", "question three", "question four"]
"""

def refine_query_prompt(sub_question: str, topic: str) -> str:
    return f"""Convert this research sub-question into an optimal ArXiv keyword search query.
Topic context: {topic}
Sub-question: {sub_question}
Respond with ONLY the search query string (no quotes, no explanation). Keep it under 8 words."""
