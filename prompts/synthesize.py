def final_report_prompt(topic: str, sub_summaries: list) -> str:
    sections = "\n\n".join([
        f"### Sub-Question: {s['question']}\n{s['summary']}"
        for s in sub_summaries
    ])
    return f"""You are a senior research scientist writing a structured literature review.

Research Topic: {topic}

Below are summaries from multiple targeted literature searches:

{sections}

Write a comprehensive, well-structured literature review report with the following sections:

# Literature Review: {topic}

## Executive Summary
(3–4 sentences capturing the state of the field)

## Key Themes & Findings
(Organized thematically, not by sub-question — synthesize across sources)

## Methodological Landscape
(What approaches dominate? What are emerging methods?)

## Research Gaps & Open Questions
(What remains unsolved or understudied?)

## Trend Analysis
(What directions is the field moving toward?)

## Conclusion
(2–3 sentences wrapping up the review)

Use **bold** for key terms. Be precise and technical. Write for an expert audience.
Do NOT just repeat the summaries — synthesize and draw connections."""
