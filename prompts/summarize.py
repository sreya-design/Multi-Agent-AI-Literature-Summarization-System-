def summarize_paper_prompt(title: str, abstract: str, sub_question: str) -> str:
    return f"""You are a research analyst. Summarize the following paper in relation to the research question.

Research Question: {sub_question}

Paper Title: {title}
Abstract: {abstract}

Provide a concise structured summary with:
1. **Core Contribution**: What does this paper contribute? (2–3 sentences)
2. **Methods**: Key techniques or approaches used (1–2 sentences)
3. **Relevance**: How does it address the research question? (1–2 sentences)
4. **Limitations**: Any noted limitations or gaps (1 sentence)

Be direct and technical. No filler phrases."""

def batch_summarize_prompt(papers_text: str, sub_question: str) -> str:
    return f"""You are a research analyst reviewing multiple papers on a specific question.

Research Question: {sub_question}

Papers:
{papers_text}

For each paper, provide:
- Title (as header)
- Core contribution (2 sentences)
- Key methods (1 sentence)
- Relevance to the question (1 sentence)

Then write a 2-sentence synthesis: What do these papers collectively reveal about the question?
Format clearly with markdown headers."""
