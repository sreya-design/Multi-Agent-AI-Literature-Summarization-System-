from typing import List, Dict, Callable, Optional
from utils.arxiv_client import search_arxiv, deduplicate_papers
from utils.gemini_client import call_gemini
from prompts.decompose import refine_query_prompt

def refine_search_query(sub_question: str, topic: str) -> str:
    """Use Gemini to convert a sub-question into an optimal ArXiv search query."""
    try:
        prompt = refine_query_prompt(sub_question, topic)
        refined = call_gemini(prompt)
        if refined and len(refined.strip()) > 3:
            return refined.strip().strip('"').strip("'")
    except Exception:
        pass
    return sub_question  # Fallback to raw sub-question

def retrieve_papers_for_question(
    sub_question: str,
    topic: str,
    max_results: int = 8,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict:
    """
    Retrieve ArXiv papers for a single sub-question.
    Returns dict with question, query used, and list of papers.
    """
    if progress_callback:
        progress_callback(f"🔍 Refining query for: *{sub_question}*")

    search_query = refine_search_query(sub_question, topic)

    if progress_callback:
        progress_callback(f"📡 Searching ArXiv: `{search_query}`")

    papers = search_arxiv(search_query, max_results=max_results)

    return {
        "question": sub_question,
        "query": search_query,
        "papers": papers,
    }

def retrieve_all_papers(
    sub_questions: List[str],
    topic: str,
    max_per_query: int = 8,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> List[Dict]:
    """
    Retrieve papers for all sub-questions, deduplicating across queries.
    Returns list of dicts: {question, query, papers}.
    """
    results = []
    all_papers_flat = []

    for i, question in enumerate(sub_questions):
        if progress_callback:
            progress_callback(f"**Step {i+1}/{len(sub_questions)}**: Retrieving papers...")

        result = retrieve_papers_for_question(
            question, topic, max_results=max_per_query, progress_callback=progress_callback
        )
        results.append(result)
        all_papers_flat.extend(result["papers"])

    # Report dedup stats
    unique_count = len(deduplicate_papers(all_papers_flat))
    if progress_callback:
        progress_callback(f"✅ Retrieved {len(all_papers_flat)} papers ({unique_count} unique) across {len(sub_questions)} queries.")

    return results
