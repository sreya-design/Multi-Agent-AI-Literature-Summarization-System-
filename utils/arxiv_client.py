import arxiv
import time
import random
from typing import List, Dict


def search_arxiv(query: str, max_results: int = 8) -> List[Dict]:
    """Search ArXiv using the official arxiv Python library."""
    try:
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=3,
            num_retries=5,
        )
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        papers = []
        for result in client.results(search):
            papers.append({
                "id": result.entry_id,
                "title": result.title.strip().replace("\n", " "),
                "abstract": result.summary.strip().replace("\n", " "),
                "authors": [a.name for a in result.authors[:5]],
                "published": str(result.published)[:10] if result.published else "Unknown",
                "url": result.entry_id,
            })
        time.sleep(2 + random.uniform(0, 2))
        return papers

    except Exception as e:
        raise RuntimeError(f"ArXiv search failed: {e}")


def deduplicate_papers(all_papers: List[Dict]) -> List[Dict]:
    """Remove duplicate papers by ArXiv ID."""
    seen = set()
    unique = []
    for p in all_papers:
        if p["id"] not in seen:
            seen.add(p["id"])
            unique.append(p)
    return unique
