from typing import List, Dict, Callable, Optional
from utils.gemini_client import call_gemini
from prompts.summarize import batch_summarize_prompt
from prompts.synthesize import final_report_prompt

def format_papers_for_prompt(papers: List[Dict]) -> str:
    """Format papers list into a text block for the prompt."""
    blocks = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:3]) or "Unknown"
        blocks.append(
            f"[Paper {i}]\n"
            f"Title: {p['title']}\n"
            f"Authors: {authors}\n"
            f"Published: {p.get('published', 'N/A')}\n"
            f"Abstract: {p['abstract'][:800]}\n"
            f"URL: {p['url']}"
        )
    return "\n\n---\n\n".join(blocks)

def summarize_papers_for_question(
    question: str,
    papers: List[Dict],
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Summarize a batch of papers for one sub-question using Gemini."""
    if not papers:
        return f"*No papers found for this question.*"

    if progress_callback:
        progress_callback(f"🧠 Summarizing {len(papers)} papers for: *{question}*")

    papers_text = format_papers_for_prompt(papers)
    prompt = batch_summarize_prompt(papers_text, question)
    summary = call_gemini(prompt)
    return summary or "*Summarization failed for this section.*"

def generate_final_report(
    topic: str,
    retrieval_results: List[Dict],
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict:
    """
    Full synthesis pipeline:
    1. Summarize papers per sub-question
    2. Generate final structured report
    Returns dict with sub_summaries and final_report.
    """
    sub_summaries = []

    for i, result in enumerate(retrieval_results):
        question = result["question"]
        papers = result["papers"]

        summary = summarize_papers_for_question(
            question, papers, progress_callback=progress_callback
        )
        sub_summaries.append({
            "question": question,
            "query": result.get("query", question),
            "papers": papers,
            "summary": summary,
        })

    if progress_callback:
        progress_callback("📝 Generating final synthesized report...")

    prompt = final_report_prompt(topic, sub_summaries)
    final_report = call_gemini(prompt)

    if not final_report:
        final_report = "# Report Generation Failed\n\nCould not generate final report. Check API key and quota."

    return {
        "topic": topic,
        "sub_summaries": sub_summaries,
        "final_report": final_report,
    }
